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
    mfi: int
    cutoff: int


@dataclass
class HLAAntibodies:
    antibodies_list: List[HLAAntibody] = field(default_factory=list)
    hla_codes_over_cutoff: List[str] = field(default_factory=list)

    def __init__(self, antibodies_list: List[HLAAntibody] = None):
        if antibodies_list is None:
            antibodies_list = []
        object.__setattr__(self, 'antibodies_list', antibodies_list)
        hla_codes_over_cutoff = [hla_antibody.code for hla_antibody in antibodies_list if
                                 hla_antibody.mfi >= hla_antibody.cutoff]
        object.__setattr__(self, 'hla_codes_over_cutoff', hla_codes_over_cutoff)


@dataclass
class PatientParameters:
    blood_group: str
    country_code: Country
    hla_typing: HLATyping = HLATyping()
