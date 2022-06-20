from datetime import datetime
from typing import List, Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.patients.patient import TxmEvent


def parse_date_to_datetime(date: Optional[str]) -> Optional[datetime]:
    if date is None:
        return None
    try:
        return datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError) as ex:
        raise InvalidArgumentException(f'Invalid date "{date}". It must be in format "YYYY-MM-DD", e.g.,'
                                       ' "2020-12-31".') from ex


def check_existing_ids_for_duplicates(txm_event: TxmEvent, donors: List[DonorUploadDTO],
                                      recipients: List[RecipientUploadDTO]):
    new_donor_ids = {donor.medical_id for donor in donors}
    current_donor_ids = {donor.medical_id for donor in txm_event.all_donors}
    donor_duplicate_ids = new_donor_ids.intersection(current_donor_ids)

    new_recipient_ids = {recipient.medical_id for recipient in recipients}
    current_recipient_ids = {recipient.medical_id for recipient in txm_event.all_recipients}
    recipient_duplicate_ids = new_recipient_ids.intersection(current_recipient_ids)
    if donor_duplicate_ids:
        raise InvalidArgumentException(f'There were the same donors in current data and in the data for upload:'
                                       f' {donor_duplicate_ids}')
    if recipient_duplicate_ids:
        raise InvalidArgumentException(f'There were the same donors in current data and in the data for upload:'
                                       f' {recipient_duplicate_ids}')
