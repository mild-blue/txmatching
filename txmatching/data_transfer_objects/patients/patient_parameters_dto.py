from dataclasses import dataclass
from typing import List, Optional

from txmatching.patients.hla_model import HLAPerGroup, HLATypeRaw
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Sex


@dataclass
class HLATypingDTO:
    hla_per_groups: List[HLAPerGroup]


@dataclass
class PatientParametersDTO:
    blood_group: BloodGroup
    country_code: Country
    hla_typing: HLATypingDTO
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    yob: Optional[int] = None


@dataclass
class HLATypingRawDTO:
    """
    List of antigens in a format as uploaded without being parsed
    """
    hla_types_list: List[HLATypeRaw]
