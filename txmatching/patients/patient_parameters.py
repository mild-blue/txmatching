from dataclasses import dataclass, field
from typing import List

from txmatching.utils.country import Country
from txmatching.utils.hla_system.hla_table import get_compatibility_broad_codes


@dataclass
class HLATyping:
    codes: List[str] = field(default_factory=list)

    @property
    def hla_typing_broad_resolution(self) -> List[str]:
        return get_compatibility_broad_codes(self.codes)


@dataclass
class HLAAntibodies:
    codes: List[str] = field(default_factory=list)

    @property
    def hla_antibodies_broad_resolution(self) -> List[str]:
        return get_compatibility_broad_codes(self.codes)


@dataclass
class PatientParameters:
    blood_group: str
    country_code: Country
    hla_typing: HLATyping = HLATyping()
