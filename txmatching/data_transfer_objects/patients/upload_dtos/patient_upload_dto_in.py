from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import StrictnessType


@dataclass
class PatientUploadDTOIn:
    country: Country
    txm_event_name: str
    donors: List[DonorUploadDTO]
    recipients: List[RecipientUploadDTO]
    add_to_existing_patients: bool = False
    strictness_type: Optional[StrictnessType] = StrictnessType.STRICT
