from dataclasses import dataclass, field
from typing import List, Optional

from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.patients.patient_parameters_dataclasses import HLAType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex


@dataclass
class HLATypingDTO:
    hla_types_list: List[HLAType] = field(default_factory=list)


@dataclass
class PatientParametersDTO:
    blood_group: BloodGroup
    country_code: Country
    hla_typing: HLATypingDTO = HLATypingDTO()
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    yob: Optional[int] = None
