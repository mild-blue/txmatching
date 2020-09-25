from dataclasses import dataclass, field
from typing import List, Optional

from txmatching.patients.patient_parameters import HLAType
from txmatching.utils.enums import Country, Sex


@dataclass
class HLATypingDTO:
    hla_types_list: List[HLAType] = field(default_factory=list)


@dataclass
class PatientParametersDTO:
    blood_group: str
    country_code: Country
    hla_typing: HLATypingDTO = HLATypingDTO()
    sex: Optional[Sex] = None
    height: Optional[int] = None
    weight: Optional[float] = None
    yob: Optional[int] = None
