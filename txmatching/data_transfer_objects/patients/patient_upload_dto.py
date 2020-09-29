from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.donor_upload_dto import DonorUploadDTO
from txmatching.data_transfer_objects.patients.recipient_upload_dto import RecipientUploadDTO


@dataclass
class PatientUploadDTO:
    country: str
    txm_event_name: str
    donors: List[DonorUploadDTO]
    recipients: List[Optional[RecipientUploadDTO]]
