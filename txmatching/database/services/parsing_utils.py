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
    new_ids = [donor.medical_id for donor in donors] + [recipient.medical_id for recipient in recipients]
    old_ids = [donor.medical_id for donor in txm_event.all_donors] + [recipient.medical_id for recipient in
                                                                      txm_event.all_recipients]

    upload_duplicate_medical_ids = _find_duplicates_in_list(new_ids)
    db_duplicate_medical_ids = set(old_ids).intersection(new_ids)

    if upload_duplicate_medical_ids:
        raise InvalidArgumentException(f'Duplicate medical ids {upload_duplicate_medical_ids} in data for upload.')

    if db_duplicate_medical_ids:
        raise InvalidArgumentException(f'Medical ids {db_duplicate_medical_ids} are already in use in given txm event.')


def _find_duplicates_in_list(list_to_check: List[str]) -> List[str]:
    seen = set()
    return {x for x in list_to_check if x in seen or seen.add(x)}
