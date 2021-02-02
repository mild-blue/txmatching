import dataclasses
import hashlib
import logging
from datetime import datetime
from typing import Optional, Union

import dacite

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingDTO
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.db import db
from txmatching.database.services.parsing_utils import get_hla_code
from txmatching.database.sql_alchemy_schema import (
    DonorModel, RecipientAcceptableBloodModel, RecipientHLAAntibodyModel,
    RecipientModel)
from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibodies,
                                           HLAAntibody, HLAPerGroup, HLAType,
                                           HLATyping)
from txmatching.patients.patient import (Donor, Patient, Recipient,
                                         RecipientRequirements, TxmEvent)
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.hla_system.hla_transformations import \
    preprocess_hla_code_in
from txmatching.utils.hla_system.hla_transformations_store import \
    parse_hla_raw_code_and_store_parsing_error_in_db
from txmatching.utils.logging_tools import PatientAdapter

logger = logging.getLogger(__name__)


def get_donor_from_donor_model(donor_model: DonorModel) -> Donor:
    base_patient = _get_base_patient_from_patient_model(donor_model)

    return Donor(base_patient.db_id,
                 base_patient.medical_id,
                 parameters=base_patient.parameters,
                 donor_type=donor_model.donor_type,
                 related_recipient_db_id=donor_model.recipient_id,
                 active=donor_model.active
                 )


def get_recipient_from_recipient_model(recipient_model: RecipientModel,
                                       related_donor_db_id: Optional[int] = None) -> Recipient:
    if not related_donor_db_id:
        related_donor_db_id = DonorModel.query.filter(DonorModel.recipient_id == recipient_model.id).one().id
    base_patient = _get_base_patient_from_patient_model(recipient_model)
    logger_with_patient = PatientAdapter(logger, {'patient_medical_id': recipient_model.medical_id})

    return Recipient(base_patient.db_id,
                     base_patient.medical_id,
                     parameters=base_patient.parameters,
                     related_donor_db_id=related_donor_db_id,
                     hla_antibodies=HLAAntibodies(
                         [HLAAntibody(code=get_hla_code(hla_antibody.code, hla_antibody.raw_code),
                                      mfi=hla_antibody.mfi,
                                      cutoff=hla_antibody.cutoff,
                                      raw_code=hla_antibody.raw_code)
                          for hla_antibody in recipient_model.hla_antibodies],
                         logger_with_patient
                     ),
                     acceptable_blood_groups=[acceptable_blood_model.blood_type for acceptable_blood_model in
                                              recipient_model.acceptable_blood],
                     recipient_cutoff=recipient_model.recipient_cutoff,
                     recipient_requirements=RecipientRequirements(**recipient_model.recipient_requirements),
                     waiting_since=recipient_model.waiting_since,
                     previous_transplants=recipient_model.previous_transplants
                     )


def update_recipient(recipient_update_dto: RecipientUpdateDTO, txm_event_db_id: int) -> Recipient:
    # TODO do not delete https://trello.com/c/zseK1Zcf
    recipient_update_dto = _update_patient_preprocessed_typing(recipient_update_dto)
    old_recipient_model = RecipientModel.query.get(recipient_update_dto.db_id)
    if txm_event_db_id != old_recipient_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient the user has no access to.')

    recipient_update_dict = {}
    if recipient_update_dto.acceptable_blood_groups:
        acceptable_blood_models = [
            RecipientAcceptableBloodModel(blood_type=blood, recipient_id=recipient_update_dto.db_id) for blood
            in
            recipient_update_dto.acceptable_blood_groups]
        RecipientAcceptableBloodModel.query.filter(
            RecipientAcceptableBloodModel.recipient_id == recipient_update_dto.db_id).delete()
        db.session.add_all(acceptable_blood_models)
    if recipient_update_dto.hla_antibodies:
        # not the best approach: in case cutoff was different per antibody before it will be unified now, but
        # but good for the moment
        old_recipient = get_recipient_from_recipient_model(old_recipient_model)
        cutoff = recipient_update_dto.cutoff if recipient_update_dto.cutoff is not None \
            else old_recipient.recipient_cutoff

        hla_antibodies = [
            RecipientHLAAntibodyModel(
                recipient_id=recipient_update_dto.db_id,
                raw_code=hla_antibody_dto.raw_code,
                mfi=hla_antibody_dto.mfi,
                cutoff=cutoff,
                code=parse_hla_raw_code_and_store_parsing_error_in_db(hla_antibody_dto.raw_code)
            ) for hla_antibody_dto in recipient_update_dto.hla_antibodies_preprocessed.hla_antibodies_list]

        RecipientHLAAntibodyModel.query.filter(
            RecipientHLAAntibodyModel.recipient_id == recipient_update_dto.db_id).delete()
        db.session.add_all(hla_antibodies)
    if recipient_update_dto.hla_typing:
        recipient_update_dict['hla_typing'] = dataclasses.asdict(recipient_update_dto.hla_typing_preprocessed)
    if recipient_update_dto.recipient_requirements:
        recipient_update_dict['recipient_requirements'] = dataclasses.asdict(
            recipient_update_dto.recipient_requirements)
    if recipient_update_dto.cutoff:
        recipient_update_dict['recipient_cutoff'] = recipient_update_dto.cutoff

    RecipientModel.query.filter(RecipientModel.id == recipient_update_dto.db_id).update(recipient_update_dict)
    db.session.commit()
    return get_recipient_from_recipient_model(RecipientModel.query.get(recipient_update_dto.db_id))


def update_donor(donor_update_dto: DonorUpdateDTO, txm_event_db_id: int) -> Donor:
    # TODO do not delete https://trello.com/c/zseK1Zcf
    donor_update_dto = _update_patient_preprocessed_typing(donor_update_dto)
    old_donor_model = DonorModel.query.get(donor_update_dto.db_id)
    if txm_event_db_id != old_donor_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient the user has no access to')

    donor_update_dict = {}
    if donor_update_dto.hla_typing:
        donor_update_dict['hla_typing'] = dataclasses.asdict(donor_update_dto.hla_typing_preprocessed)
    if donor_update_dto.active is not None:
        donor_update_dict['active'] = donor_update_dto.active
    DonorModel.query.filter(DonorModel.id == donor_update_dto.db_id).update(donor_update_dict)
    db.session.commit()
    return get_donor_from_donor_model(DonorModel.query.get(donor_update_dto.db_id))


def get_patients_hash(txm_event: TxmEvent) -> int:
    donors = tuple(txm_event.active_donors_dict.values()) \
        if txm_event.active_donors_dict is not None else None
    recipients = tuple(txm_event.active_recipients_dict.values()) \
        if txm_event.active_recipients_dict is not None else None

    hash_ = hashlib.md5()
    _update_hash(hash_, donors)
    _update_hash(hash_, recipients)
    hash_int = int(hash_.hexdigest(), 16) % 2**63  # convert to int8
    return hash_int


# pylint: disable=too-many-branches, too-many-statements
# Many branches and statements are still readable here
def _update_hash(hash_, value):
    type_str = f'__{type(value).__name__}__'
    hash_.update(type_str.encode('ASCII'))

    if isinstance(value, str):
        hash_.update(value.encode('ASCII'))
    elif isinstance(value, (int, bool, float, datetime)):
        _update_hash(hash_, str(value))
    elif isinstance(value, (list, set, tuple)):
        for item in value:
            _update_hash(hash_, item)
    elif isinstance(value, dict):
        for key, val in value.items():
            _update_hash(hash_, key)
            _update_hash(hash_, val)
    elif value is None:
        _update_hash(hash_, '__none__')
    elif isinstance(value, Patient):
        _update_hash(hash_, value.medical_id)
        _update_hash(hash_, value.parameters)
        if isinstance(value, Donor):
            _update_hash(hash_, value.related_recipient_db_id)
            _update_hash(hash_, value.donor_type)
            _update_hash(hash_, value.active)
        if isinstance(value, Recipient):
            _update_hash(hash_, value.related_donor_db_id)
            _update_hash(hash_, sorted(value.acceptable_blood_groups))
            _update_hash(hash_, value.recipient_cutoff)
            _update_hash(hash_, value.hla_antibodies)
            _update_hash(hash_, value.recipient_requirements)
            _update_hash(hash_, value.waiting_since)
            _update_hash(hash_, value.previous_transplants)
    elif isinstance(value, PatientParameters):
        _update_hash(hash_, value.blood_group)
        _update_hash(hash_, value.country_code)
        _update_hash(hash_, value.hla_typing)
        _update_hash(hash_, value.sex)
        _update_hash(hash_, value.height)
        _update_hash(hash_, value.weight)
        _update_hash(hash_, value.year_of_birth)
    elif isinstance(value, HLATyping):
        _update_hash(hash_, value.hla_per_groups)
    elif isinstance(value, HLAPerGroup):
        _update_hash(hash_, value.hla_group)
        _update_hash(hash_, sorted(value.hla_types, key=lambda hla_type: hla_type.raw_code))
    elif isinstance(value, HLAType):
        _update_hash(hash_, value.raw_code)
    elif isinstance(value, RecipientRequirements):
        # Treat None as False
        _update_hash(hash_, bool(value.require_better_match_in_compatibility_index_or_blood_group))
        _update_hash(hash_, bool(value.require_better_match_in_compatibility_index))
        _update_hash(hash_, bool(value.require_compatible_blood_group))
    elif isinstance(value, HLAAntibodies):
        _update_hash(hash_, value.hla_antibodies_per_groups)
    elif isinstance(value, AntibodiesPerGroup):
        _update_hash(hash_, value.hla_group)
        _update_hash(hash_, sorted(value.hla_antibody_list,
                                   key=lambda hla_type: (
                                      hla_type.raw_code,
                                      hla_type.mfi,
                                      hla_type.cutoff
                                  )))
    elif isinstance(value, HLAAntibody):
        _update_hash(hash_, value.raw_code)
        _update_hash(hash_, value.mfi)
        _update_hash(hash_, value.cutoff)
    else:
        raise NotImplementedError(f'Hashing type {type(value)} ({value}) not implemented')


def _get_base_patient_from_patient_model(patient_model: Union[DonorModel, RecipientModel]) -> Patient:
    return Patient(
        db_id=patient_model.id,
        medical_id=patient_model.medical_id,
        parameters=PatientParameters(
            blood_group=patient_model.blood,
            country_code=patient_model.country,
            hla_typing=dacite.from_dict(data_class=HLATyping, data=patient_model.hla_typing),
            height=patient_model.height,
            weight=patient_model.weight,
            year_of_birth=patient_model.yob,
            sex=patient_model.sex
        ))


def _update_patient_preprocessed_typing(patient_update: PatientUpdateDTO) -> PatientUpdateDTO:
    """
    Updates u patient's hla typing.
    This method is partially redundant to PatientUpdateDTO.__post_init__ so in case of update, update it too.
    :param patient_update: patient to be updated
    :return: updated patient
    """
    if patient_update.hla_typing:
        patient_update.hla_typing_preprocessed = HLATypingDTO([
            HLAType(
                raw_code=preprocessed_code,
                code=parse_hla_raw_code_and_store_parsing_error_in_db(preprocessed_code)
            )
            for hla_type_update_dto in patient_update.hla_typing.hla_types_list
            for preprocessed_code in preprocess_hla_code_in(hla_type_update_dto.raw_code)
        ])
    return patient_update
