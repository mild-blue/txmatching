from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_upload_dto import HLAAntibodiesUploadDTO
from txmatching.utils.enums import Sex


@dataclass
class RecipientUploadDTO:
    # pylint: disable=too-many-instance-attributes
    acceptable_blood_groups: Optional[List[str]]
    medical_id: str
    blood_group: str
    HLA_typing: List[str]  # pylint: disable=invalid-name
    HLA_antibodies: List[HLAAntibodiesUploadDTO]  # pylint: disable=invalid-name
    sex: Optional[Sex]
    height: Optional[int]
    weight: Optional[int]
    YOB: Optional[int]  # pylint: disable=invalid-name
    waiting_since: Optional[str]
    previous_transplants: Optional[int]
