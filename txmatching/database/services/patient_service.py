import dataclasses
import logging
from enum import Enum
from typing import List, Optional, Tuple, Union

import dacite

from txmatching.auth.exceptions import (InvalidArgumentException,
                                        OverridingException)
from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssue
from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesDTO
from txmatching.data_transfer_objects.patients.patient_parameters_dto import (
    HLATypingDTO, HLATypingRawDTO)
from txmatching.data_transfer_objects.patients.patient_upload_dto_out import \
    PatientsRecomputeParsingSuccessDTOOut
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.db import db
from txmatching.database.services.parsing_issue_service import (
    convert_parsing_issue_models_to_dataclasses,
    delete_parsing_issues_for_patient, delete_parsing_issues_for_txm_event_id,
    get_parsing_issues_for_txm_event_id, parsing_issues_bases_to_models)
from txmatching.database.services.parsing_utils import parse_date_to_datetime
from txmatching.database.sql_alchemy_schema import (
    DonorModel, HLAAntibodyRawModel, RecipientAcceptableBloodModel,
    RecipientModel)
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibodies,
                                           HLAAntibody, HLAAntibodyRaw,
                                           HLATypeRaw, HLATyping)
from txmatching.patients.patient import (Donor, Patient, Recipient,
                                         RecipientRequirements, TxmEvent)
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.enums import HLAGroup
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import (
    parse_hla_antibodies_raw_and_return_parsing_issue_list,
    parse_hla_typing_raw_and_return_parsing_issue_list)
from txmatching.utils.persistent_hash import (get_hash_digest,
                                              initialize_persistent_hash,
                                              update_persistent_hash)

logger = logging.getLogger(__name__)


def get_donor_from_donor_model(donor_model: DonorModel) -> Donor:
    base_patient = _get_base_patient_from_patient_model(donor_model)

    return Donor(base_patient.db_id,
                 base_patient.medical_id,
                 parameters=base_patient.parameters,
                 etag=base_patient.etag,
                 donor_type=donor_model.donor_type,
                 related_recipient_db_id=donor_model.recipient_id,
                 active=donor_model.active,
                 internal_medical_id=donor_model.internal_medical_id,
                 parsing_issues=convert_parsing_issue_models_to_dataclasses(donor_model.parsing_issues)
                 )


def get_recipient_from_recipient_model(recipient_model: RecipientModel) -> Recipient:
    related_donors_db_ids = [donor.id for donor in DonorModel.query.filter(
        DonorModel.recipient_id == recipient_model.id).all()]
    base_patient = _get_base_patient_from_patient_model(recipient_model)

    recipient = Recipient(base_patient.db_id,
                          base_patient.medical_id,
                          parameters=base_patient.parameters,
                          etag=base_patient.etag,
                          related_donors_db_ids=related_donors_db_ids,
                          hla_antibodies=get_hla_antibodies_from_recipient_model(recipient_model),
                          # TODO: https://github.com/mild-blue/txmatching/issues/477 represent blood as enum,
                          #       this conversion is not working properly now
                          acceptable_blood_groups=[acceptable_blood_model.blood_type for acceptable_blood_model in
                                                   recipient_model.acceptable_blood],
                          recipient_cutoff=recipient_model.recipient_cutoff,
                          recipient_requirements=RecipientRequirements(**recipient_model.recipient_requirements),
                          waiting_since=recipient_model.waiting_since,
                          previous_transplants=recipient_model.previous_transplants,
                          internal_medical_id=recipient_model.internal_medical_id,
                          parsing_issues=convert_parsing_issue_models_to_dataclasses(recipient_model.parsing_issues)
                          )
    return recipient


def get_hla_antibodies_from_recipient_model(recipient_model: RecipientModel) -> HLAAntibodies:
    antibodies_dto = HLAAntibodiesDTO([
                                AntibodiesPerGroup(hla_group=hla["hla_group"],
                                                   hla_antibody_list=[HLAAntibody(
                                                    raw_code=antibody['raw_code'],
                                                    mfi=antibody["mfi"],
                                                    cutoff=antibody["cutoff"],
                                                    code=HLACode(high_res=antibody["code"]["high_res"],
                                                                split=antibody["code"]["split"],
                                                                broad=antibody["code"]["broad"],
                                                                group=HLAGroup(antibody["code"]["group"]))
                                                   ) for antibody in hla["hla_antibody_list"]])
                                for hla in recipient_model.hla_antibodies['hla_antibodies_per_groups']])

    antibodies_raw_models = recipient_model.hla_antibodies_raw
    antibodies_raw = [
        HLAAntibodyRaw(
            raw_code=antibody_raw_model.raw_code,
            mfi=antibody_raw_model.mfi,
            cutoff=antibody_raw_model.cutoff
        ) for antibody_raw_model in antibodies_raw_models
    ]

    if antibodies_dto.hla_antibodies_per_groups is None:
        raise ValueError(f'Parsed antibodies have invalid format. '
                         f'Running recompute-parsing api could help: ${antibodies_dto}')
    return HLAAntibodies(
        hla_antibodies_raw_list=sorted(
            antibodies_raw,
            key=lambda hla_type: (
                hla_type.raw_code,
            )),
        hla_antibodies_per_groups=antibodies_dto.hla_antibodies_per_groups
    )


def _get_hla_typing_from_patient_model(
        patient_model: Union[DonorModel, RecipientModel],
) -> HLATyping:
    hla_typing_dto: HLATypingDTO = dacite.from_dict(
        data_class=HLATypingDTO, data=patient_model.hla_typing,
        config=dacite.Config(cast=[Enum])
    )

    hla_typing_raw_dto: HLATypingRawDTO = dacite.from_dict(
        data_class=HLATypingRawDTO, data=patient_model.hla_typing_raw,
        config=dacite.Config(cast=[Enum])
    )

    if hla_typing_dto.hla_per_groups is None:
        raise ValueError(f'Parsed antigens have invalid format. '
                         f'Running recompute-parsing api could help: ${hla_typing_dto}')
    return HLATyping(
        hla_types_raw_list=hla_typing_raw_dto.hla_types_list,
        hla_per_groups=hla_typing_dto.hla_per_groups,
    )


def _create_patient_update_dict_base(patient_update_dto: PatientUpdateDTO) -> Tuple[List[ParsingIssue], dict]:
    patient_update_dict = {}
    parsing_issues = []
    if patient_update_dto.blood_group is not None:
        patient_update_dict['blood'] = patient_update_dto.blood_group
    if patient_update_dto.hla_typing is not None:
        hla_typing_raw = HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(hla_type.raw_code) for hla_type in patient_update_dto.hla_typing.hla_types_list]
        )
        patient_update_dict['hla_typing_raw'] = dataclasses.asdict(hla_typing_raw)
        parsing_issues, hla_typing_dict = parse_hla_typing_raw_and_return_parsing_issue_list(
            hla_typing_raw
        )
        patient_update_dict['hla_typing'] = dataclasses.asdict(hla_typing_dict)

    # For the following parameters we support setting null value
    patient_update_dict['sex'] = patient_update_dto.sex
    patient_update_dict['height'] = patient_update_dto.height
    patient_update_dict['weight'] = patient_update_dto.weight
    patient_update_dict['yob'] = patient_update_dto.year_of_birth
    patient_update_dict['etag'] = patient_update_dto.etag + 1

    if patient_update_dto.note is not None:
        patient_update_dict['note'] = patient_update_dto.note

    return parsing_issues, patient_update_dict


def update_recipient(recipient_update_dto: RecipientUpdateDTO, txm_event_db_id: int) -> Recipient:
    old_recipient_model = RecipientModel.query.get(recipient_update_dto.db_id)
    parsing_issues = []

    if recipient_update_dto.recipient_requirements:
        _check_if_recipient_requirements_are_valid(recipient_update_dto.recipient_requirements)

    if txm_event_db_id != old_recipient_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient from a different txm event.')

    updated_parsing_issues, recipient_update_dict = _create_patient_update_dict_base(recipient_update_dto)
    updated_parsing_issues = parsing_issues_bases_to_models(parsing_issues_temp=updated_parsing_issues,
                                                            recipient_id=old_recipient_model.id,
                                                            txm_event_id=old_recipient_model.txm_event_id)

    if old_recipient_model.etag != recipient_update_dict['etag'] - 1:
        raise OverridingException('The patient can\'t be updated, someone edited this patient in the meantime.')

    delete_parsing_issues_for_patient(recipient_id=old_recipient_model.id,
                                      txm_event_id=old_recipient_model.txm_event_id)

    parsing_issues = parsing_issues + updated_parsing_issues
    if recipient_update_dto.acceptable_blood_groups:
        acceptable_blood_models = [
            RecipientAcceptableBloodModel(blood_type=blood, recipient_id=recipient_update_dto.db_id) for blood
            in
            recipient_update_dto.acceptable_blood_groups]
        RecipientAcceptableBloodModel.query.filter(
            RecipientAcceptableBloodModel.recipient_id == recipient_update_dto.db_id).delete()
        db.session.add_all(acceptable_blood_models)

    if recipient_update_dto.hla_antibodies or recipient_update_dto.cutoff:
        # not the best approach: in case cutoff was different per antibody before it will be unified now, but
        # but good for the moment
        if recipient_update_dto.cutoff is not None:
            recipient_update_dict['recipient_cutoff'] = recipient_update_dto.cutoff
            new_cutoff = recipient_update_dto.cutoff
        else:
            new_cutoff = old_recipient_model.recipient_cutoff

        # hla_antibodies_raw will be updated
        # - with new hla antibodies and new cutoff (if update hla antibodies are specified)
        # - or with old hla antibodies from db and new cutoff (if only cutoff is specified)
        hla_antibodies_raw_source = recipient_update_dto.hla_antibodies.hla_antibodies_list \
            if recipient_update_dto.hla_antibodies is not None \
            else old_recipient_model.hla_antibodies_raw
        new_hla_antibody_raw_models = [
            HLAAntibodyRawModel(
                recipient_id=recipient_update_dto.db_id,
                raw_code=hla_antibody.raw_code,
                cutoff=new_cutoff,
                mfi=hla_antibody.mfi,
            ) for hla_antibody in hla_antibodies_raw_source
        ]

        # Change hla_antibodies_raw for a given patient in db
        HLAAntibodyRawModel.query.filter(
            HLAAntibodyRawModel.recipient_id == recipient_update_dto.db_id
        ).delete()
        db.session.add_all(new_hla_antibody_raw_models)

        # Change parsed hla_antibodies for a given patient in db
        antibody_parsing_issues, hla_antibodies = parse_hla_antibodies_raw_and_return_parsing_issue_list(
            new_hla_antibody_raw_models,
        )
        updated_parsing_issues = parsing_issues_bases_to_models(parsing_issues_temp=antibody_parsing_issues,
                                                                recipient_id=old_recipient_model.id,
                                                                txm_event_id=old_recipient_model.txm_event_id)
        parsing_issues = parsing_issues + updated_parsing_issues
        recipient_update_dict['hla_antibodies'] = dataclasses.asdict(hla_antibodies)

    db.session.add_all(parsing_issues)
    if recipient_update_dto.recipient_requirements:
        recipient_update_dict['recipient_requirements'] = dataclasses.asdict(
            recipient_update_dto.recipient_requirements)
    recipient_update_dict['waiting_since'] = parse_date_to_datetime(recipient_update_dto.waiting_since)
    recipient_update_dict['previous_transplants'] = recipient_update_dto.previous_transplants

    RecipientModel.query.filter(RecipientModel.id == recipient_update_dto.db_id).update(recipient_update_dict)
    db.session.commit()
    return get_recipient_from_recipient_model(
        RecipientModel.query.get(recipient_update_dto.db_id))


def update_donor(donor_update_dto: DonorUpdateDTO, txm_event_db_id: int) -> Donor:
    old_donor_model = DonorModel.query.get(donor_update_dto.db_id)
    if txm_event_db_id != old_donor_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient from a different txm event.')

    parsing_issues, donor_update_dict = _create_patient_update_dict_base(donor_update_dto)
    parsing_issues = parsing_issues_bases_to_models(parsing_issues_temp=parsing_issues,
                                                    donor_id=old_donor_model.id,
                                                    txm_event_id=old_donor_model.txm_event_id)

    if old_donor_model.etag != donor_update_dict['etag'] - 1:
        raise OverridingException('The patient can\'t be saved, someone edited this patient in the meantime.')

    delete_parsing_issues_for_patient(donor_id=old_donor_model.id,
                                      txm_event_id=old_donor_model.txm_event_id)

    db.session.add_all(parsing_issues)
    if donor_update_dto.active is not None:
        donor_update_dict['active'] = donor_update_dto.active
    DonorModel.query.filter(DonorModel.id == donor_update_dto.db_id).update(donor_update_dict)
    db.session.commit()
    return get_donor_from_donor_model(DonorModel.query.get(donor_update_dto.db_id))


def recompute_hla_and_antibodies_parsing_for_all_patients_in_txm_event(
        txm_event_id: int
) -> PatientsRecomputeParsingSuccessDTOOut:
    result = PatientsRecomputeParsingSuccessDTOOut(
        patients_checked_antigens=0,
        patients_changed_antigens=0,
        patients_checked_antibodies=0,
        patients_changed_antibodies=0,
        parsing_issues=[],
    )
    # Clear parsing issues table
    delete_parsing_issues_for_txm_event_id(txm_event_id)

    # Get donors and recipients
    donor_models = DonorModel.query.filter(DonorModel.txm_event_id == txm_event_id).all()
    recipient_models = RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event_id).all()

    # Update hla_typing for donors and recipients
    for patient_model in donor_models + recipient_models:
        hla_typing_raw = dacite.from_dict(data_class=HLATypingRawDTO, data=patient_model.hla_typing_raw)
        patient_parsing_issues, hla_typing = parse_hla_typing_raw_and_return_parsing_issue_list(hla_typing_raw)
        if patient_model in donor_models:
            new_parsing_issues = parsing_issues_bases_to_models(parsing_issues_temp=patient_parsing_issues,
                                                                donor_id=patient_model.id,
                                                                txm_event_id=patient_model.txm_event_id)
        else:
            new_parsing_issues = parsing_issues_bases_to_models(parsing_issues_temp=patient_parsing_issues,
                                                                recipient_id=patient_model.id,
                                                                txm_event_id=patient_model.txm_event_id)
        db.session.add_all(new_parsing_issues)
        patient_model.parsing_issues = new_parsing_issues
        new_hla_typing = dataclasses.asdict(hla_typing)

        if new_hla_typing != patient_model.hla_typing:
            logger.debug(f'Updating hla_typing of {patient_model}:')
            patient_model.hla_typing = new_hla_typing
            result.patients_changed_antigens += 1

        result.patients_checked_antigens += 1

    # Update hla_antibodies for recipients
    for recipient_model in recipient_models:
        hla_antibodies_raw = recipient_model.hla_antibodies_raw
        patient_parsing_issues, hla_antibodies = parse_hla_antibodies_raw_and_return_parsing_issue_list(
            hla_antibodies_raw)
        new_parsing_issues = parsing_issues_bases_to_models(parsing_issues_temp=patient_parsing_issues,
                                                            recipient_id=recipient_model.id,
                                                            txm_event_id=recipient_model.txm_event_id)
        new_hla_antibodies = dataclasses.asdict(hla_antibodies)
        db.session.add_all(new_parsing_issues)
        recipient_model.parsing_issues = recipient_model.parsing_issues + new_parsing_issues
        if new_hla_antibodies != recipient_model.hla_antibodies:
            logger.debug(f'Updating hla_antibodies of {recipient_model}:')
            recipient_model.hla_antibodies = new_hla_antibodies
            result.patients_changed_antibodies += 1

        result.patients_checked_antibodies += 1

    db.session.commit()

    # Get parsing issues
    result.parsing_issues = get_parsing_issues_for_txm_event_id(txm_event_id)

    return result


def get_patients_persistent_hash(txm_event: TxmEvent) -> int:
    donors = tuple(txm_event.active_and_valid_donors_dict.values())
    recipients = tuple(txm_event.active_and_valid_recipients_dict.values())

    hash_ = initialize_persistent_hash()
    update_persistent_hash(hash_, donors)
    update_persistent_hash(hash_, recipients)
    hash_digest = get_hash_digest(hash_)

    return hash_digest


def get_all_patients_persistent_hash(txm_event: TxmEvent) -> int:
    donors = tuple(txm_event.all_donors)
    recipients = tuple(txm_event.all_recipients)

    hash_ = initialize_persistent_hash()
    update_persistent_hash(hash_, donors)
    update_persistent_hash(hash_, recipients)
    hash_digest = get_hash_digest(hash_)

    return hash_digest


def _get_base_patient_from_patient_model(patient_model: Union[DonorModel, RecipientModel]) -> Patient:
    return Patient(
        db_id=patient_model.id,
        medical_id=patient_model.medical_id,
        parameters=PatientParameters(
            # TODO: https://github.com/mild-blue/txmatching/issues/477 represent blood by enum,
            #       this conversion is not working properly now
            blood_group=patient_model.blood,
            country_code=patient_model.country,
            hla_typing=_get_hla_typing_from_patient_model(patient_model),
            height=patient_model.height,
            weight=patient_model.weight,
            year_of_birth=patient_model.yob,
            sex=patient_model.sex,
            note=patient_model.note
        ),
        etag=patient_model.etag
    )


def get_donor_recipient_pair(donor_id: int, txm_event_id: int) -> Tuple[Donor, Optional[Recipient]]:
    donor_model = DonorModel.query.get(donor_id)  # type: DonorModel
    if donor_model is None or donor_model.txm_event_id != txm_event_id:
        raise InvalidArgumentException(f'Donor {donor_id} not found in txm event {txm_event_id}')
    donor = get_donor_from_donor_model(donor_model)
    recipient_id = donor_model.recipient_id

    if recipient_id is not None:
        recipient_model = RecipientModel.query.get(recipient_id)  # type: RecipientModel
        maybe_recipient = get_recipient_from_recipient_model(recipient_model)
    else:
        maybe_recipient = None

    return donor, maybe_recipient


def delete_donor_recipient_pair(donor_id: int, txm_event_id: int):
    _, maybe_recipient = get_donor_recipient_pair(donor_id, txm_event_id)

    delete_parsing_issues_for_patient(donor_id=donor_id, txm_event_id=txm_event_id)
    DonorModel.query.filter(DonorModel.id == donor_id).delete()

    if (maybe_recipient is not None and
            len(maybe_recipient.related_donors_db_ids) == 1):
        delete_parsing_issues_for_patient(recipient_id=maybe_recipient.db_id, txm_event_id=txm_event_id)
        RecipientModel.query.filter(RecipientModel.id == maybe_recipient.db_id).delete()

    db.session.commit()


def _check_if_recipient_requirements_are_valid(recipient_requirements: RecipientRequirements):
    if (recipient_requirements.min_donor_age and recipient_requirements.max_donor_age and
            recipient_requirements.min_donor_age > recipient_requirements.max_donor_age):
        raise InvalidArgumentException(f'Maximal required age {recipient_requirements.max_donor_age} is smaller than '
                                       f'minimal required age {recipient_requirements.min_donor_age}.')

    if (recipient_requirements.min_donor_height and recipient_requirements.max_donor_height and
            recipient_requirements.min_donor_height > recipient_requirements.max_donor_height):
        raise InvalidArgumentException(f'Maximal required height {recipient_requirements.max_donor_height} is smaller '
                                       f'than minimal required height {recipient_requirements.min_donor_height}.')

    if (recipient_requirements.min_donor_weight and recipient_requirements.max_donor_weight and
            recipient_requirements.min_donor_weight > recipient_requirements.max_donor_weight):
        raise InvalidArgumentException(f'Maximal required weight {recipient_requirements.max_donor_weight} is smaller '
                                       f'than minimal required weight {recipient_requirements.min_donor_weight}.')


def raise_error_if_donor_in_txm_event_doesnt_exist(txm_event_id: int, donor_id: int):
    donor_model = DonorModel.query.get(donor_id)
    if donor_model is None or donor_model.txm_event_id != txm_event_id:
        raise InvalidArgumentException(f'Donor {donor_id} not found in txm event {txm_event_id}')
