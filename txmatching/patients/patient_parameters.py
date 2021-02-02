from dataclasses import dataclass
from typing import Optional

from txmatching.patients.hla_model import HLATyping
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex

Kilograms = float
Centimeters = int


@dataclass(unsafe_hash=True)
class PatientParameters:
    blood_group: BloodGroup
    country_code: Country
    hla_typing: HLATyping
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
