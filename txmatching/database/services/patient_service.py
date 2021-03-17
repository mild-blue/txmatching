import dataclasses
import logging
from enum import Enum
from typing import Optional, Tuple, Union

import dacite

from txmatching.auth.exceptions import InvalidArgumentException
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
from txmatching.database.services.parsing_utils import parse_date_to_datetime
from txmatching.database.sql_alchemy_schema import (
    DonorModel, HLAAntibodyRawModel, ParsingErrorModel,
    RecipientAcceptableBloodModel, RecipientModel)
from txmatching.patients.hla_model import (HLAAntibodies, HLAAntibodyRaw,
                                           HLATypeRaw, HLATyping)
from txmatching.patients.patient import (Donor, Patient, Recipient,
                                         RecipientRequirements, TxmEvent)
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.hla_system.hla_transformations_store import (
    parse_hla_antibodies_raw_and_add_parsing_error_to_db_session,
    parse_hla_typing_raw_and_add_parsing_error_to_db_session)
from txmatching.utils.logging_tools import PatientAdapter
from txmatching.utils.persistent_hash import (get_hash_digest,
                                              initialize_persistent_hash,
                                              update_persistent_hash)

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

    recipient = Recipient(base_patient.db_id,
                          base_patient.medical_id,
                          parameters=base_patient.parameters,
                          related_donor_db_id=related_donor_db_id,
                          hla_antibodies=get_hla_antibodies_from_recipient_model(recipient_model),
                          # TODO: https://github.com/mild-blue/txmatching/issues/477 represent blood as enum,
                          #       this conversion is not working properly now
                          acceptable_blood_groups=[acceptable_blood_model.blood_type for acceptable_blood_model in
                                                   recipient_model.acceptable_blood],
                          recipient_cutoff=recipient_model.recipient_cutoff,
                          recipient_requirements=RecipientRequirements(**recipient_model.recipient_requirements),
                          waiting_since=recipient_model.waiting_since,
                          previous_transplants=recipient_model.previous_transplants
                          )
    return recipient


def get_hla_antibodies_from_recipient_model(
        recipient_model: RecipientModel,
) -> HLAAntibodies:
    antibodies_dto: HLAAntibodiesDTO = dacite.from_dict(
        data_class=HLAAntibodiesDTO, data=recipient_model.hla_antibodies,
        config=dacite.Config(cast=[Enum])
    )

    antibodies_raw_models = recipient_model.hla_antibodies_raw
    antibodies_raw = [
        HLAAntibodyRaw(
            raw_code=antibody_raw_model.raw_code,
            mfi=antibody_raw_model.mfi,
            cutoff=antibody_raw_model.cutoff
        ) for antibody_raw_model in antibodies_raw_models
    ]

    if antibodies_dto.hla_antibodies_list is None or antibodies_dto.hla_antibodies_per_groups is None:
        raise ValueError(f'Parsed antibodies have invalid format. '
                         f'Running recompute-parsing api could help: ${antibodies_dto}')
    return HLAAntibodies(
        hla_antibodies_list=antibodies_dto.hla_antibodies_list,
        hla_antibodies_raw_list=antibodies_raw,
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


def _create_patient_update_dict_base(patient_update_dto: PatientUpdateDTO) -> dict:
    patient_update_dict = {}

    if patient_update_dto.blood_group is not None:
        patient_update_dict['blood'] = patient_update_dto.blood_group
    if patient_update_dto.hla_typing is not None:
        hla_typing_raw = HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(hla_type.raw_code) for hla_type in patient_update_dto.hla_typing.hla_types_list]
        )
        patient_update_dict['hla_typing_raw'] = dataclasses.asdict(hla_typing_raw)
        patient_update_dict['hla_typing'] = dataclasses.asdict(
            parse_hla_typing_raw_and_add_parsing_error_to_db_session(
                hla_typing_raw
            )
        )

    # For the following parameters we support setting null value
    patient_update_dict['sex'] = patient_update_dto.sex
    patient_update_dict['height'] = patient_update_dto.height
    patient_update_dict['weight'] = patient_update_dto.weight
    patient_update_dict['yob'] = patient_update_dto.year_of_birth

    return patient_update_dict


def update_recipient(recipient_update_dto: RecipientUpdateDTO, txm_event_db_id: int) -> Recipient:
    old_recipient_model = RecipientModel.query.get(recipient_update_dto.db_id)
    if txm_event_db_id != old_recipient_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient the user has no access to.')

    recipient_update_dict = _create_patient_update_dict_base(recipient_update_dto)
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
        logger_with_patient = PatientAdapter(logger, {'patient_medical_id': old_recipient_model.medical_id})
        hla_antibodies = parse_hla_antibodies_raw_and_add_parsing_error_to_db_session(
            new_hla_antibody_raw_models,
            logger_with_patient
        )
        recipient_update_dict['hla_antibodies'] = dataclasses.asdict(hla_antibodies)

    if recipient_update_dto.recipient_requirements:
        recipient_update_dict['recipient_requirements'] = dataclasses.asdict(
            recipient_update_dto.recipient_requirements)
    recipient_update_dict['waiting_since'] = parse_date_to_datetime(recipient_update_dto.waiting_since)
    recipient_update_dict['previous_transplants'] = recipient_update_dto.previous_transplants

    RecipientModel.query.filter(RecipientModel.id == recipient_update_dto.db_id).update(recipient_update_dict)
    db.session.commit()
    return get_recipient_from_recipient_model(RecipientModel.query.get(recipient_update_dto.db_id))


def update_donor(donor_update_dto: DonorUpdateDTO, txm_event_db_id: int) -> Donor:
    old_donor_model = DonorModel.query.get(donor_update_dto.db_id)
    if txm_event_db_id != old_donor_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient the user has no access to')

    donor_update_dict = _create_patient_update_dict_base(donor_update_dto)
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
        parsing_errors=[],
    )

    # Clear parsing errors table
    ParsingErrorModel.query.delete()

    # Get donors and recipients
    donor_models = DonorModel.query.filter(DonorModel.txm_event_id == txm_event_id).all()
    recipient_models = RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event_id).all()

    # Update hla_typing for donors and recipients
    for patient_model in donor_models + recipient_models:
        hla_typing_raw = dacite.from_dict(data_class=HLATypingRawDTO, data=patient_model.hla_typing_raw)
        new_hla_typing = dataclasses.asdict(
            parse_hla_typing_raw_and_add_parsing_error_to_db_session(
                hla_typing_raw
            )
        )

        if new_hla_typing != patient_model.hla_typing:
            logger.debug(f'Updating hla_typing of {patient_model}:')
            patient_model.hla_typing = new_hla_typing
            result.patients_changed_antigens += 1

        result.patients_checked_antigens += 1

    # Update hla_antibodies for recipients
    for recipient_model in recipient_models:
        hla_antibodies_raw = recipient_model.hla_antibodies_raw
        logger_with_patient = PatientAdapter(logger, {'patient_medical_id': recipient_model.medical_id})
        new_hla_antibodies = dataclasses.asdict(
            parse_hla_antibodies_raw_and_add_parsing_error_to_db_session(hla_antibodies_raw, logger_with_patient)
        )

        if new_hla_antibodies != recipient_model.hla_antibodies:
            logger.debug(f'Updating hla_antibodies of {recipient_model}:')
            recipient_model.hla_antibodies = new_hla_antibodies
            result.patients_changed_antibodies += 1

        result.patients_checked_antibodies += 1

    db.session.commit()

    # Get parsing errors
    parsing_error_models = ParsingErrorModel.query.all()
    result.parsing_errors = [
        {
            'hla_code': parsing_error_model.hla_code,
            'hla_code_processing_result_detail': parsing_error_model.hla_code_processing_result_detail
        } for parsing_error_model in parsing_error_models
    ]

    return result


def get_patients_persistent_hash(txm_event: TxmEvent) -> int:
    donors = tuple(txm_event.active_donors_dict.values())
    recipients = tuple(txm_event.active_recipients_dict.values())

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
            sex=patient_model.sex
        ))


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
    donor, maybe_recipient = get_donor_recipient_pair(donor_id, txm_event_id)

    DonorModel.query.filter(DonorModel.id == donor.db_id).delete()
    if maybe_recipient is not None:
        RecipientModel.query.filter(RecipientModel.id == maybe_recipient.db_id).delete()

    db.session.commit()
