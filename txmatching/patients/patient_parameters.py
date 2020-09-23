from dataclasses import dataclass, field
from typing import List

from txmatching.utils.country import Country
from txmatching.utils.hla_system.hla_table import get_compatibility_broad_codes


@dataclass
class HLATyping:
    codes: List[str] = field(default_factory=list)

    @property
    def compatibility_broad_resolution_codes(self) -> List[str]:
        return get_compatibility_broad_codes(self.codes)


@dataclass
class HLAAntibody:
    code: str
    value: int
    cut_off: int


@dataclass
class HLAAntibodies:
    codes: List[HLAAntibody] = field(default_factory=list)

    @property
    def compatibility_broad_resolution_codes(self) -> List[str]:
        return get_compatibility_broad_codes([code.code for code in self.codes])


@dataclass
class PatientParameters:
    blood_group: str
    country_code: Country
    hla_typing: HLATyping = HLATyping()
