from dataclasses import dataclass, field
from typing import List, Optional

from txmatching.patients.hla_model import HLAPerGroup, HLAType
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Sex


@dataclass
class HLATypingDTO:
    # The field does not have default value because want dacite to raise exception if data stored in db are not valid
    hla_types_list: List[HLAType]
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
class HLATypeRaw:
    """
    Antigen in a format as uploaded without being parsed
    """
    raw_code: str


@dataclass
class HLATypingRawDTO:
    """
    List of antigens in a format as uploaded without being parsed
    """
    hla_types_list: List[HLATypeRaw]
