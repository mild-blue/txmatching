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

    donor_recipient_duplicate_ids = new_donor_ids.intersection(new_recipient_ids)
    new_donor_current_recipient_duplicate_ids = new_donor_ids.intersection(current_recipient_ids)
    new_recipient_current_donor_duplicate_ids = new_recipient_ids.intersection(current_donor_ids)

    new_donor_medical_id_duplicates = _find_duplicates_in_list([donor.medical_id for donor in donors])
    new_recipient_medical_id_duplicates = _find_duplicates_in_list([recipient.medical_id for recipient in recipients])

    if new_donor_medical_id_duplicates:
        raise InvalidArgumentException(f'Duplicate donor medical ids {new_recipient_medical_id_duplicates}'
                                       f' in data for upload')
    if new_recipient_medical_id_duplicates:
        raise InvalidArgumentException(f'Duplicate recipient medical ids {new_recipient_medical_id_duplicates}'
                                       f' in data for upload')
    if donor_recipient_duplicate_ids:
        raise InvalidArgumentException(f'Donor medical id {donor_recipient_duplicate_ids} is the same as recipient'
                                       f' medical id {donor_recipient_duplicate_ids}')
    if donor_duplicate_ids:
        raise InvalidArgumentException(f'There were the same donors in current data and in the data for upload:'
                                       f' {donor_duplicate_ids}')
    if recipient_duplicate_ids:
        raise InvalidArgumentException(f'There were the same recipients in current data and in the data for upload:'
                                       f' {recipient_duplicate_ids}')
    if new_donor_current_recipient_duplicate_ids:
        raise InvalidArgumentException(f'Donor medical id {new_donor_current_recipient_duplicate_ids}'
                                       f' is already in use by a recipient in given txm event')
    if new_recipient_current_donor_duplicate_ids:
        raise InvalidArgumentException(f'Recipient medical id {new_recipient_current_donor_duplicate_ids}'
                                       f' is already in use by a donor in given txm event')


def _find_duplicates_in_list(list_to_check: List[str]) -> List[str]:
    return [item for item in set(list_to_check) if list_to_check.count(item) > 1]
