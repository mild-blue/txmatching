from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.patients.patient import (is_height_valid, is_number_of_previous_transplants_valid,
    is_weight_valid, is_year_of_birth_valid)
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex


@dataclass
class RecipientUploadDTO:
    # pylint: disable=too-many-instance-attributes
    acceptable_blood_groups: Optional[List[BloodGroup]]
    medical_id: str
    blood_group: BloodGroup
    hla_typing: List[str]
    hla_antibodies: List[HLAAntibodiesUploadDTO]
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
    note: str = ''
    waiting_since: Optional[str] = None
    previous_transplants: Optional[int] = None
    internal_medical_id: Optional[str] = None

    def __post_init__(self):
        if self.height:
            is_height_valid("recipient", self.height)

        if self.weight:
            is_weight_valid("recipient", self.weight)

        if self.year_of_birth:
            is_year_of_birth_valid("recipient", self.year_of_birth)

        if self.previous_transplants:
            is_number_of_previous_transplants_valid(self.previous_transplants)
