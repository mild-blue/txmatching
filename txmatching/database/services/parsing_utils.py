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


# pylint: disable=too-many-locals
def check_existing_ids_for_duplicates(txm_event: TxmEvent, donors: List[DonorUploadDTO],
                                      recipients: List[RecipientUploadDTO]):
    # get medical ids
    new_donor_ids = {donor.medical_id for donor in donors}
    new_recipient_ids = {recipient.medical_id for recipient in recipients}
    current_donor_ids = {donor.medical_id for donor in txm_event.all_donors}
    current_recipient_ids = {recipient.medical_id for recipient in txm_event.all_recipients}

    # find duplicates
    donor_duplicate_ids = new_donor_ids.intersection(current_donor_ids)
    recipient_duplicate_ids = new_recipient_ids.intersection(current_recipient_ids)
    donor_recipient_duplicate_ids = new_donor_ids.intersection(new_recipient_ids)
    new_donor_current_recipient_duplicate_ids = new_donor_ids.intersection(current_recipient_ids)
    new_recipient_current_donor_duplicate_ids = new_recipient_ids.intersection(current_donor_ids)
    new_donor_medical_id_duplicates = _find_duplicates_in_list([donor.medical_id for donor in donors])
    new_recipient_medical_id_duplicates = _find_duplicates_in_list([recipient.medical_id for recipient in recipients])

    # union all duplicate ids
    db_duplicate_medical_ids = donor_duplicate_ids.union(recipient_duplicate_ids,
                                                         new_donor_current_recipient_duplicate_ids,
                                                         new_recipient_current_donor_duplicate_ids)

    new_patient_duplicates = set(new_donor_medical_id_duplicates + new_recipient_medical_id_duplicates)
    upload_duplicate_medical_ids = donor_recipient_duplicate_ids.union(new_patient_duplicates)

    if upload_duplicate_medical_ids:
        raise InvalidArgumentException(f'Duplicate medical ids {upload_duplicate_medical_ids} in data for upload.')

    if db_duplicate_medical_ids:
        raise InvalidArgumentException(f'Medical ids {db_duplicate_medical_ids} are already in use in given txm event.')


def _find_duplicates_in_list(list_to_check: List[str]) -> List[str]:
    return [item for item in set(list_to_check) if list_to_check.count(item) > 1]
