import itertools
from dataclasses import dataclass, field
from typing import List, Optional

from txmatching.patients.patient_parameters_dataclasses import HLAType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import (CodesPerGroup, Country, Sex,
                                    split_to_hla_groups)
from txmatching.utils.hla_system.hla_transformations import (
    get_mfi_from_multiple_hla_codes, parse_hla_raw_code)

Kilograms = float
Centimeters = int

# TODOO: move back HLAType maybe


@dataclass
class HLATyping:
    hla_types_list: List[HLAType]
    codes_per_group: Optional[List[CodesPerGroup]] = None

    def __post_init__(self):
        if self.codes_per_group is None:
            codes = [hla_type for hla_type in self.hla_types_list if hla_type.code]
            self.codes_per_group = split_to_hla_groups(codes)


@dataclass
class HLAAntibody:
    raw_code: str
    mfi: int
    cutoff: int
    code: Optional[str] = None

    def __post_init__(self):
        if self.code is None:
            code = parse_hla_raw_code(self.raw_code)
            self.code = code


@dataclass
class HLAAntibodies:
    hla_antibodies_list: List[HLAAntibody] = field(default_factory=list)
    hla_codes_over_cutoff_per_group: List[CodesPerGroup] = field(default_factory=list)

    def __init__(self, hla_antibodies_list: List[HLAAntibody] = None):
        if hla_antibodies_list is None:
            hla_antibodies_list = []
        self.hla_antibodies_list = hla_antibodies_list
        hla_antibodies_list_without_none = [hla_antibody for hla_antibody in hla_antibodies_list if hla_antibody.code]
        grouped_hla_codes = itertools.groupby(
            sorted(hla_antibodies_list_without_none, key=lambda hla_code: (hla_code.code, hla_code.cutoff)),
            key=lambda hla_code: (hla_code.code, hla_code.cutoff)
        )
        hla_codes_over_cutoff_list = []
        for (hla_code_name, hla_code_cutoff), hla_code_group in grouped_hla_codes:
            hla_code_group_list = list(hla_code_group)
            assert len(hla_code_group_list) > 0
            mfi = get_mfi_from_multiple_hla_codes([hla_code.mfi for hla_code in hla_code_group_list])
            if mfi >= hla_code_cutoff:
                hla_codes_over_cutoff_list.append(
                    HLAType(
                        raw_code=hla_code_group_list[0].raw_code,
                        code=hla_code_group_list[0].code,
                    )
                )

        self.hla_codes_over_cutoff_per_group = split_to_hla_groups(hla_codes_over_cutoff_list)


@dataclass
class PatientParameters:
    blood_group: BloodGroup
    country_code: Country
    hla_typing: HLATyping
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
