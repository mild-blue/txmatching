import datetime
from typing import List, Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.upload_dto.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dto.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.patients.patient import TxmEvent
from txmatching.utils.hla_system.hla_transformations import parse_hla_raw_code


def parse_date_to_datetime(date: Optional[str]) -> Optional[datetime.datetime]:
    if date is None:
        return None
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError) as ex:
        raise InvalidArgumentException(f'Invalid date "{date}". It must be in format "YYYY-MM-DD", e.g.,'
                                       ' "2020-12-31".') from ex


def get_hla_code(code: Optional[str], raw_code: str) -> Optional[str]:
    return code if code is not None else parse_hla_raw_code(raw_code)


def check_existing_ids_for_duplicates(txm_event: TxmEvent, donors: List[DonorUploadDTO],
                                      recipients: List[RecipientUploadDTO]):
    new_donor_ids = {donor.medical_id for donor in donors}
    current_donor_ids = {donor.medical_id for donor in txm_event.all_donors}
    donor_duplicate_ids = new_donor_ids.intersection(current_donor_ids)

    new_recipient_ids = {recipient.medical_id for recipient in recipients}
    current_recipient_ids = {recipient.medical_id for recipient in txm_event.all_recipients}
    recipient_duplicate_ids = new_recipient_ids.intersection(current_recipient_ids)
    if donor_duplicate_ids or recipient_duplicate_ids:
        raise InvalidArgumentException(f'There were the same patients in current data and in the data for upload:'
                                       f' duplicate donor ids: {donor_duplicate_ids};'
                                       f' duplicate recipient ids {recipient_duplicate_ids}')
