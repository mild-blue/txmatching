from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.patients.hla_antibodies_upload_dto import HLAAntibodiesUploadDTO


@dataclass
class RecipientUploadDTO:
    # pylint: disable=too-many-instance-attributes
    acceptable_blood_groups: List[str]
    medical_id: str
    blood_group: str
    hla_typing: List[str]
    hla_antibodies: List[HLAAntibodiesUploadDTO]
    sex: str
    height: int
    weight: int
    yob: int
    waiting_since: str
    previous_transplants: int
