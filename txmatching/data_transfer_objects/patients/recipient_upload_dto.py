from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.enums import Sex


@dataclass
class RecipientUploadDTO:
    # pylint: disable=too-many-instance-attributes
    acceptable_blood_groups: Optional[List[str]]
    medical_id: str
    blood_group: str
    hla_typing: List[str]
    hla_antibodies: List[HLAAntibodiesUploadDTO]
    sex: Optional[Sex]
    height: Optional[Centimeters]
    weight: Optional[Kilograms]
    year_of_birth: Optional[int]
    waiting_since: Optional[str]
    previous_transplants: Optional[int]
