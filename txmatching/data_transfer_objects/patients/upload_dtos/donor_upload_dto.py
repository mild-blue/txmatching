from dataclasses import dataclass
from typing import List, Optional

from txmatching.patients.patient import is_height_valid, is_weight_valid, is_year_of_birth_valid
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex


@dataclass
class DonorUploadDTO:
    # pylint: disable=too-many-instance-attributes
    medical_id: str
    blood_group: BloodGroup
    hla_typing: List[str]
    donor_type: str
    related_recipient_medical_id: Optional[str]
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
    note: str = ''
    internal_medical_id: Optional[str] = None

    def __post_init__(self):
        if self.height:
            is_height_valid("donor", self.height)

        if self.weight:
            is_weight_valid("donor", self.weight)

        if self.year_of_birth:
            is_year_of_birth_valid("donor", self.year_of_birth)
