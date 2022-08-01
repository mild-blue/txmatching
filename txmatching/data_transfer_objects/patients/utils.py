import logging
from typing import Optional

from txmatching.data_transfer_objects.hla.parsing_issue_dto import (
    ParsingIssue, ParsingIssuePublicDTO)
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.sql_alchemy_schema import ParsingIssueModel
from txmatching.patients.patient import Donor, Recipient, TxmEventBase

logger = logging.getLogger(__name__)


# is needed here because kw_args in dataclass is not handled well by pylint
# pylint: disable=unexpected-keyword-arg
def parsing_issue_to_dto(parsing_issue: ParsingIssue, txm_event: TxmEventBase) -> ParsingIssuePublicDTO:
    return ParsingIssuePublicDTO(
        hla_code_or_group=parsing_issue.hla_code_or_group,
        parsing_issue_detail=parsing_issue.parsing_issue_detail,
        message=parsing_issue.message,
        txm_event_name=txm_event.name,
        medical_id=_get_donor_or_recipient_medical_id(parsing_issue, txm_event)
    )


def parsing_issue_model_to_parsing_issue(parsing_issue: ParsingIssueModel) -> ParsingIssue:
    return ParsingIssue(
        db_id=parsing_issue.id,
        hla_code_or_group=parsing_issue.hla_code_or_group,
        parsing_issue_detail=parsing_issue.parsing_issue_detail,
        message=parsing_issue.message,
        donor_id=parsing_issue.donor_id,
        recipient_id=parsing_issue.recipient_id,
        txm_event_id=parsing_issue.id,
        confirmed_by=parsing_issue.confirmed_by,
        confirmed_at=parsing_issue.confirmed_at,
    )


def _get_donor_or_recipient_medical_id(parsing_issue: ParsingIssue, txm_event) -> Optional[str]:
    if parsing_issue.donor_id:
        medical_ids = [donor.medical_id for donor in txm_event.all_donors if donor.db_id == parsing_issue.donor_id]
    elif parsing_issue.recipient_id:
        medical_ids = [recipient.medical_id for recipient in txm_event.all_recipients if
                       recipient.db_id == parsing_issue.recipient_id]
    else:
        logger.error('None was returned as medical id of patient, because neither donor id'
                     'nor recipient id was provided for the parsing issue. This should never happen,'
                     'it probably means that some wrong formatting of parsing issue was used.')
        return None

    if len(medical_ids) == 1:
        return medical_ids[0]
    else:
        logger.error('None was returned as medical id of patient in parsing issue object this should never'
                     ' happen as there should always be exactly one recipient or donor with given medical id for'
                     ' txm event. If this happens it likely means wrong txm event was provided')
        return None


def donor_to_donor_upload_dto(donor: Donor) -> DonorUploadDTO:
    return DonorUploadDTO(
        medical_id=donor.medical_id,
        blood_group=donor.parameters.blood_group,
        hla_typing=[code.raw_code for code in donor.parameters.hla_typing.hla_types_raw_list],
        donor_type=donor.donor_type,
        related_recipient_medical_id=donor.related_recipient_db_id,
        sex=donor.parameters.sex,
        height=donor.parameters.height,
        weight=donor.parameters.weight,
        year_of_birth=donor.parameters.year_of_birth,
        note=donor.parameters.note,
        internal_medical_id=donor.internal_medical_id)


def recipient_to_recipient_upload_dto(recipient: Recipient) -> RecipientUploadDTO:
    return RecipientUploadDTO(
        acceptable_blood_groups=recipient.acceptable_blood_groups,
        medical_id=recipient.medical_id,
        blood_group=recipient.parameters.blood_group,
        hla_typing=[code.raw_code for code in recipient.parameters.hla_typing.hla_types_raw_list],
        hla_antibodies=[HLAAntibodiesUploadDTO(
            cutoff=code.cutoff,
            mfi=code.mfi,
            name=code.raw_code
        ) for code in recipient.hla_antibodies.hla_antibodies_raw_list],
        sex=recipient.parameters.sex,
        height=recipient.parameters.height,
        weight=recipient.parameters.weight,
        year_of_birth=recipient.parameters.year_of_birth,
        note=recipient.parameters.note,
        previous_transplants=recipient.previous_transplants,
        internal_medical_id=recipient.internal_medical_id)