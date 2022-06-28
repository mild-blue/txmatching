from typing import List

from txmatching.data_transfer_objects.patients.upload_dtos.donor_recipient_pair_upload_dtos import \
    DonorRecipientPairDTO
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.data_transfer_objects.patients.utils import (
    donor_to_donor_upload_dto, recipient_to_recipient_upload_dto)
from txmatching.database.db import db
from txmatching.database.services.patient_upload_service import \
    add_donor_recipient_pair_uncommitted
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete


def copy_patients_between_events(txm_event_id_from: int, txm_event_id_to: int, donor_ids: List[int]) -> List[int]:
    txm_event_from = get_txm_event_complete(txm_event_id_from, load_antibodies_raw=True)
    new_donor_ids = []

    for donor_id in donor_ids:
        donor = txm_event_from.active_and_valid_donors_dict[donor_id]
        related_recipient_id = donor.related_recipient_db_id
        donor_country = donor.parameters.country_code

        donor_upload_dto = donor_to_donor_upload_dto(donor)

        if related_recipient_id is not None:
            recipient = txm_event_from.active_and_valid_recipients_dict[related_recipient_id]
            recipient_upload_dto = recipient_to_recipient_upload_dto(recipient)
        else:
            recipient_upload_dto = None

        donor_recipient_pair = DonorRecipientPairDTO(
            country_code=donor_country,
            donor=donor_upload_dto,
            recipient=recipient_upload_dto
        )

        donor, recipient = add_donor_recipient_pair_uncommitted(donor_recipient_pair, txm_event_id_to)

    db.session.commit()

    txm_event_to = get_txm_event_complete(txm_event_id_to, load_antibodies_raw=True)
    new_donor_ids = [donor.db_id for donor in txm_event_to.active_and_valid_donors_dict.values()]

    return new_donor_ids
