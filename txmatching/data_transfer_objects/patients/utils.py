import logging
from typing import Optional

from txmatching.data_transfer_objects.hla.parsing_issue_dto import (
    ParsingIssue, ParsingIssuePublicDTO)
from txmatching.database.sql_alchemy_schema import ParsingIssueModel
from txmatching.patients.patient import TxmEventBase

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
