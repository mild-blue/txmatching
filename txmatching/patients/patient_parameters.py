import itertools
from dataclasses import dataclass, field
from typing import List, Optional

from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex
from txmatching.utils.hla_system.hla_transformations import (
    get_compatibility_broad_codes, get_mfi_from_multiple_hla_codes,
    parse_hla_raw_code)

Kilograms = float
Centimeters = int


@dataclass
class HLAType:
    raw_code: str
    code: Optional[str] = None

    def __post_init__(self):
        if self.code is None:
            code = parse_hla_raw_code(self.raw_code)
            object.__setattr__(self, 'code', code)


@dataclass
class HLATyping:
    hla_types_list: List[HLAType] = field(default_factory=list)
    codes: Optional[List[str]] = None

    def __post_init__(self):
        if self.codes is None:
            codes = [hla_type.code for hla_type in self.hla_types_list]
            object.__setattr__(self, 'codes', codes)

    @property
    def compatibility_broad_resolution_codes(self) -> List[str]:
        return get_compatibility_broad_codes(self.codes)


@dataclass
class HLAAntibody:
    raw_code: str
    mfi: int
    cutoff: int
    code: Optional[str] = None

    def __post_init__(self):
        if self.code is None:
            code = parse_hla_raw_code(self.raw_code)
            object.__setattr__(self, 'code', code)


@dataclass
class HLAAntibodies:
    hla_antibodies_list: List[HLAAntibody] = field(default_factory=list)
    hla_codes_over_cutoff: List[str] = field(default_factory=list)

    def __init__(self, hla_antibodies_list: List[HLAAntibody] = None):
        if hla_antibodies_list is None:
            hla_antibodies_list = []
        object.__setattr__(self, 'hla_antibodies_list', hla_antibodies_list)
        hla_antibodies_list_without_none = [hla_antibody for hla_antibody in hla_antibodies_list if hla_antibody.code]
        grouped_hla_codes = itertools.groupby(
            sorted(hla_antibodies_list_without_none, key=lambda hla_code: (hla_code.code, hla_code.cutoff)),
            key=lambda hla_code: (hla_code.code, hla_code.cutoff)
        )
        hla_codes_over_cutoff = []
        for (hla_code_name, hla_code_cutoff), hla_code_group in grouped_hla_codes:
            mfi = get_mfi_from_multiple_hla_codes([hla_code.mfi for hla_code in hla_code_group])
            if mfi >= hla_code_cutoff:
                hla_codes_over_cutoff.append(hla_code_name)
        object.__setattr__(self, 'hla_codes_over_cutoff', hla_codes_over_cutoff)


@dataclass
class PatientParameters:
    blood_group: BloodGroup
    country_code: Country
    hla_typing: HLATyping = HLATyping()
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
