import dataclasses
import logging
from typing import Dict, List, Tuple

import dacite

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.hla.parsing_issue_dto import (
    ParsingIssue, ParsingIssuePublicDTO)
from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingRawDTO
from txmatching.data_transfer_objects.patients.upload_dtos.donor_recipient_pair_upload_dtos import \
    DonorRecipientPairDTO
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.data_transfer_objects.patients.utils import \
    parsing_issue_to_dto
from txmatching.database.db import db
from txmatching.database.services.parsing_utils import (
    check_existing_ids_for_duplicates, parse_date_to_datetime)
from txmatching.database.services.patient_service import \
    get_hla_antibodies_from_recipient_model
from txmatching.database.services.txm_event_service import (
    get_txm_event_complete, get_txm_event_db_id_by_name,
    remove_donors_and_recipients_from_txm_event_for_country)
from txmatching.database.sql_alchemy_schema import (
    DonorModel, HLAAntibodyRawModel, RecipientAcceptableBloodModel,
    RecipientModel)
from txmatching.patients.hla_model import HLATypeRaw
from txmatching.patients.patient import DonorType, calculate_cutoff
from txmatching.utils.country_enum import Country
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import (
    parse_hla_antibodies_raw_and_return_parsing_issue_list,
    parse_hla_typing_raw_and_return_parsing_issue_list)
from txmatching.database.services.parsing_issue_service import (
    get_parsing_issues_for_patients, parsing_issues_to_models)

logger = logging.getLogger(__name__)


def add_donor_recipient_pair(donor_recipient_pair_dto: DonorRecipientPairDTO,
                             txm_event_db_id: int) -> Tuple[List[DonorModel], List[RecipientModel]]:
    if donor_recipient_pair_dto.recipient:
        donor_recipient_pair_dto.donor.related_recipient_medical_id = donor_recipient_pair_dto.recipient.medical_id

    donors, recipients = _add_patients_from_one_country(
        donors=[donor_recipient_pair_dto.donor],
        recipients=[donor_recipient_pair_dto.recipient] if donor_recipient_pair_dto.recipient else [],
        country_code=donor_recipient_pair_dto.country_code,
        txm_event_db_id=txm_event_db_id
    )
    db.session.commit()
    return donors, recipients


def get_patients_parsing_issues_from_upload_dto(donors: List[DonorModel], recipients: List[RecipientModel],
                                        txm_event_db_id: int) -> List[ParsingIssuePublicDTO]:
    donor_ids = [patient.id for patient in donors]
    recipient_ids = [patient.id for patient in recipients]
    parsing_issues = get_parsing_issues_for_patients(txm_event_db_id, donor_ids, recipient_ids)
    txm_event = get_txm_event_complete(txm_event_db_id)

    return [parsing_issue_to_dto(parsing_issue, txm_event) for parsing_issue in parsing_issues]


def get_patients_parsing_issues_from_pair_dto(donors: List[DonorModel], recipients: List[RecipientModel],
                                      txm_event_db_id: int) -> List[ParsingIssuePublicDTO]:
    donor_ids = [donors[0].id]
    recipient_ids = []
    if len(recipients) > 0:
        recipient_ids.append(recipients[0].id)
    parsing_issues = get_parsing_issues_for_patients(txm_event_db_id, donor_ids, recipient_ids)
    txm_event = get_txm_event_complete(txm_event_db_id)
    return [parsing_issue_to_dto(parsing_issue, txm_event) for parsing_issue in parsing_issues]


def replace_or_add_patients_from_one_country(patient_upload_dto: PatientUploadDTOIn
                                             ) -> Tuple[List[DonorModel], List[RecipientModel]]:
    txm_event_db_id = get_txm_event_db_id_by_name(patient_upload_dto.txm_event_name)
    if not patient_upload_dto.add_to_existing_patients:
        remove_donors_and_recipients_from_txm_event_for_country(txm_event_db_id,
                                                                patient_upload_dto.country)

    donors, recipients = _add_patients_from_one_country(
        donors=patient_upload_dto.donors,
        recipients=patient_upload_dto.recipients,
        country_code=patient_upload_dto.country,
        txm_event_db_id=txm_event_db_id
    )
    db.session.commit()
    return donors, recipients


def replace_or_add_patients_from_excel(patient_upload_dtos: List[PatientUploadDTOIn]):
    for patient_upload_dto in patient_upload_dtos:
        replace_or_add_patients_from_one_country(patient_upload_dto)


def _recipient_upload_dto_to_recipient_model(
        recipient: RecipientUploadDTO,
        country_code: Country,
        txm_event_db_id: int
) -> RecipientModel:
    acceptable_blood_groups = [] if recipient.acceptable_blood_groups is None \
        else recipient.acceptable_blood_groups

    recipient_model = RecipientModel(
        medical_id=recipient.medical_id,
        country=country_code,
        blood=recipient.blood_group,
        hla_typing_raw=dataclasses.asdict(HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(raw_code) for raw_code in recipient.hla_typing]
        )),
        hla_antibodies_raw=[
            HLAAntibodyRawModel(
                raw_code=hla_antibody.name,
                cutoff=hla_antibody.cutoff,
                mfi=hla_antibody.mfi
            ) for hla_antibody in recipient.hla_antibodies
        ],
        acceptable_blood=[RecipientAcceptableBloodModel(blood_type=blood)
                          for blood in acceptable_blood_groups],
        txm_event_id=txm_event_db_id,
        waiting_since=parse_date_to_datetime(recipient.waiting_since),
        weight=recipient.weight,
        height=recipient.height,
        sex=recipient.sex,
        yob=recipient.year_of_birth,
        note=recipient.note,
        previous_transplants=recipient.previous_transplants,
        internal_medical_id=recipient.internal_medical_id
    )
    hla_typing_parsing_issues = _parse_and_update_hla_typing_in_model(recipient_model=recipient_model)
    hla_antibodies_parsing_issues = _parse_and_update_hla_antibodies_in_model(recipient_model)
    parsing_issues = hla_typing_parsing_issues + hla_antibodies_parsing_issues
    parsing_issues = parsing_issues_to_models(
        parsing_issues=parsing_issues,
        txm_event_id=recipient_model.txm_event_id)
    recipient_model.parsing_issues = parsing_issues
    recipient_model.etag = 1
    return recipient_model


def _parse_and_update_hla_typing_in_model(donor_model: DonorModel = None, recipient_model: RecipientModel = None) -> \
        List[ParsingIssue]:
    if donor_model is not None:
        hla_typing_raw = dacite.from_dict(data_class=HLATypingRawDTO, data=donor_model.hla_typing_raw)
        parsing_issues, hla_typing = parse_hla_typing_raw_and_return_parsing_issue_list(hla_typing_raw)
        donor_model.hla_typing = dataclasses.asdict(hla_typing)
    else:
        hla_typing_raw = dacite.from_dict(data_class=HLATypingRawDTO, data=recipient_model.hla_typing_raw)
        parsing_issues, hla_typing = parse_hla_typing_raw_and_return_parsing_issue_list(hla_typing_raw)
        recipient_model.hla_typing = dataclasses.asdict(hla_typing)
    return parsing_issues


def _parse_and_update_hla_antibodies_in_model(recipient_model: RecipientModel) -> List[ParsingIssue]:
    hla_antibodies_raw = recipient_model.hla_antibodies_raw
    parsing_issues, hla_antibodies_parsed = parse_hla_antibodies_raw_and_return_parsing_issue_list(
        hla_antibodies_raw
    )
    recipient_model.hla_antibodies = dataclasses.asdict(hla_antibodies_parsed)
    transformed_hla_antibodies = get_hla_antibodies_from_recipient_model(recipient_model)
    recipient_model.recipient_cutoff = calculate_cutoff(transformed_hla_antibodies.hla_antibodies_raw_list)
    return parsing_issues


def _donor_upload_dto_to_donor_model(
        donor: DonorUploadDTO,
        recipient_models_dict: Dict[str, RecipientModel],
        country_code: Country,
        txm_event_db_id: int
) -> DonorModel:
    maybe_related_recipient = recipient_models_dict.get(donor.related_recipient_medical_id, None)

    if donor.donor_type == DonorType.DONOR and not donor.related_recipient_medical_id:
        raise InvalidArgumentException(
            f'When recipient is not set, donor type must be "{DonorType.BRIDGING_DONOR}" or "{DonorType.NON_DIRECTED}" '
            f'but was "{donor.donor_type}".'
        )
    if (donor.donor_type == DonorType.DONOR and
            donor.related_recipient_medical_id and
            maybe_related_recipient is None):
        raise InvalidArgumentException(
            f'Donor (medical id "{donor.medical_id}") has related recipient (medical id '
            f'"{donor.related_recipient_medical_id}"), which was not found among recipients.'
        )

    if donor.donor_type != DonorType.DONOR and donor.related_recipient_medical_id is not None:
        raise InvalidArgumentException(f'When recipient is set, donor type must be "{DonorType.DONOR}" but was '
                                       f'{donor.donor_type}.')

    maybe_related_recipient_medical_id = maybe_related_recipient.medical_id if maybe_related_recipient else None

    assert (donor.related_recipient_medical_id is None or
            maybe_related_recipient_medical_id == donor.related_recipient_medical_id), \
        f'Donor requires recipient medical id "{donor.related_recipient_medical_id}", ' \
        f'but received "{maybe_related_recipient_medical_id}" or related recipient must be None.'

    donor_model = DonorModel(
        medical_id=donor.medical_id,
        country=country_code,
        blood=donor.blood_group,
        hla_typing_raw=dataclasses.asdict(HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(raw_code) for raw_code in donor.hla_typing]
        )),
        active=True,
        recipient=maybe_related_recipient,
        donor_type=donor.donor_type,
        weight=donor.weight,
        height=donor.height,
        sex=donor.sex,
        yob=donor.year_of_birth,
        note=donor.note,
        txm_event_id=txm_event_db_id,
        internal_medical_id=donor.internal_medical_id
    )

    parsing_issues = _parse_and_update_hla_typing_in_model(donor_model=donor_model)
    parsing_issues = parsing_issues_to_models(
        parsing_issues=parsing_issues,
        txm_event_id=donor_model.txm_event_id)
    donor_model.parsing_issues = parsing_issues
    donor_model.etag = 1
    return donor_model


def _add_patients_from_one_country(
        donors: List[DonorUploadDTO],
        recipients: List[RecipientUploadDTO],
        country_code: Country,
        txm_event_db_id: int
) -> Tuple[List[DonorModel], List[RecipientModel]]:
    txm_event = get_txm_event_complete(txm_event_db_id)

    check_existing_ids_for_duplicates(txm_event, donors, recipients)

    txm_event_db_id = txm_event.db_id
    recipient_models = [
        _recipient_upload_dto_to_recipient_model(recipient, country_code, txm_event_db_id)
        for recipient in recipients
    ]
    db.session.add_all(recipient_models)

    recipient_models_dict = {recipient_model.medical_id: recipient_model for recipient_model in recipient_models}

    donor_models = [
        _donor_upload_dto_to_donor_model(
            donor=donor,
            recipient_models_dict=recipient_models_dict,
            country_code=country_code,
            txm_event_db_id=txm_event_db_id)
        for donor in donors
    ]
    db.session.add_all(donor_models)

    return (donor_models, recipient_models)
