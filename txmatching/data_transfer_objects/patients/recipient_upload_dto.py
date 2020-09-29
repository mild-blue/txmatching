from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_upload_dto import HLAAntibodiesUploadDTO


@dataclass
class RecipientUploadDTO:
    # pylint: disable=too-many-instance-attributes
    acceptable_blood_groups: Optional[List[str]]
    medical_id: str
    blood_group: str
    hla_typing: List[str]
    hla_antibodies: List[HLAAntibodiesUploadDTO]
    sex: Optional[str]
    height: Optional[int]
    weight: Optional[int]
    yob: Optional[int]
    waiting_since: Optional[str]
    previous_transplants: Optional[int]
