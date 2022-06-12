from typing import List

from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.donor_recipient_pair_upload_dtos import \
    DonorRecipientPairDTO
from txmatching.patients.patient import Donor, TxmEvent
from txmatching.database.services.patient_upload_service import add_donor_recipient_pair
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.data_transfer_objects.patients.utils import donor_to_donor_upload_dto, recipient_to_recipient_upload_dto


def copy_patients_between_events(txm_event_id_from: int, txm_event_id_to:int, donor_ids: list) -> List[int]:
    txm_event_from = get_txm_event_complete(txm_event_id_from, load_antibodies_raw=True) # type: TxmEvent
    new_donor_ids = []

    for donor_id in donor_ids:
        donor = txm_event_from.active_and_valid_donors_dict[donor_id] # type: Donor
        related_recipient_id = donor.related_recipient_db_id
        donor_country = donor.parameters.country_code

        donor_upload_dto = donor_to_donor_upload_dto(donor) # type: DonorUploadDTO

        if related_recipient_id is not None:
            recipient = txm_event_from.active_and_valid_recipients_dict[related_recipient_id]
            recipient_upload_dto = recipient_to_recipient_upload_dto(recipient) # type: RecipientUploadDTO

        donor_recipient_pair = DonorRecipientPairDTO(
            country_code=donor_country,
            donor=donor_upload_dto,
            recipient=recipient_upload_dto
        )

        copied_donor = add_donor_recipient_pair(donor_recipient_pair, txm_event_id_to)
        new_donor_ids.append(copied_donor[0][0].id)

    return new_donor_ids
