from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.patients.upload_dto.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dto.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.utils.enums import Country


@dataclass
class PatientUploadDTOIn:
    country: Country
    txm_event_name: str
    donors: List[DonorUploadDTO]
    recipients: List[RecipientUploadDTO]
