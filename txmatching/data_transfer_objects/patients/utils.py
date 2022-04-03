import logging
from typing import Optional

from txmatching.data_transfer_objects.hla.parsing_error_dto import (
    ParsingError, ParsingErrorDTO)
from txmatching.patients.patient import TxmEvent

logger = logging.getLogger(__name__)


def parsing_error_to_dto(parsing_error: ParsingError, txm_event: TxmEvent) -> ParsingErrorDTO:
    return ParsingErrorDTO(
        hla_code_or_group=parsing_error.hla_code_or_group,
        parsing_issue_detail=parsing_error.parsing_issue_detail,
        message=parsing_error.message,
        txm_event_name=txm_event.name,
        medical_id=_get_donor_or_recipient_medical_id(parsing_error, txm_event)
    )


def _get_donor_or_recipient_medical_id(parsing_error: ParsingError, txm_event) -> Optional[str]:
    if parsing_error.donor_id:
        medical_ids = [donor.medical_id for donor in txm_event.all_donors if donor.db_id == parsing_error.donor_id]
    elif parsing_error.recipient_id:
        medical_ids = [recipient.medical_id for recipient in txm_event.all_recipients if
                       recipient.db_id == parsing_error.recipient_id]
    else:
        logger.error('None was returned as medical id of patient, because neither donor id'
                     'nor recipient id was provided for the parsing error. This should never happen,'
                     'it probably means that some wrong formatting of parsing error was used.')
        return None

    if len(medical_ids) == 1:
        return medical_ids[0]
    else:
        logger.error('None was returned as medical id of patient in parsing error object this should never'
                     ' happen as there should always be exactly one recipient or donor with given medical id for'
                     ' txm event. If this happens it likely means wrong txm event was provided')
        return None
