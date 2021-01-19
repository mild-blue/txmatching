import itertools
import re
from dataclasses import dataclass, field
from typing import List, Optional

from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import (HLA_GROUP_SPLIT_CODE_REGEX,
                                    HLA_GROUPS_NAMES_WITH_OTHER, Country,
                                    HLAGroup, Sex)
from txmatching.utils.hla_system.hla_transformations import (
    get_mfi_from_multiple_hla_codes, parse_hla_raw_code)

Kilograms = float
Centimeters = int


@dataclass
class HLAType:
    raw_code: str
    code: Optional[str] = None

    def __post_init__(self):
        if self.code is None:
            code = parse_hla_raw_code(self.raw_code)
            self.code = code

    def __eq__(self, other):
        """
        Needed for List[HLAType].remove()
        """
        return isinstance(other, HLAType) and self.code == other.code

    def __hash__(self):
        return hash(self.code)


@dataclass
class HLAPerGroup:
    hla_group: HLAGroup
    hla_types: List[HLAType]


@dataclass
class HLATyping:
    hla_types_list: List[HLAType]
    hla_per_groups: Optional[List[HLAPerGroup]] = None

    def __post_init__(self):
        if self.hla_per_groups is None:
            hla_types = [hla_type for hla_type in self.hla_types_list if hla_type.code]
            self.hla_per_groups = split_hla_types_to_groups(hla_types)


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

    def __eq__(self, other):
        return (isinstance(other, HLAAntibody) and
                self.code == other.code and
                self.mfi == other.mfi and
                self.raw_code == other.raw_code)

    def __hash__(self):
        return hash((self.code, self.mfi, self.raw_code))


@dataclass
class AntibodiesPerGroup:
    hla_group: HLAGroup
    hla_antibody_list: List[HLAAntibody]


@dataclass
class HLAAntibodies:
    hla_antibodies_list: List[HLAAntibody] = field(default_factory=list)
    hla_antibodies_per_groups: List[AntibodiesPerGroup] = field(default_factory=list)

    def __init__(self, hla_antibodies_list: List[HLAAntibody] = None):
        if hla_antibodies_list is None:
            hla_antibodies_list = []
        self.hla_antibodies_list = hla_antibodies_list
        hla_antibodies_list_without_none = [hla_antibody for hla_antibody in hla_antibodies_list if hla_antibody.code]
        grouped_hla_antibodies = itertools.groupby(
            sorted(hla_antibodies_list_without_none, key=lambda hla_antibody: (hla_antibody.code, hla_antibody.cutoff)),
            key=lambda hla_antibody: (hla_antibody.code, hla_antibody.cutoff)
        )
        hla_antibodies_over_cutoff_list = []
        for (_, antibody_cutoff), antibody_group in grouped_hla_antibodies:
            antibody_group_list = list(antibody_group)
            assert len(antibody_group_list) > 0
            mfi = get_mfi_from_multiple_hla_codes([hla_code.mfi for hla_code in antibody_group_list])
            if mfi >= antibody_cutoff:
                hla_antibodies_over_cutoff_list.append(
                    antibody_group_list[0]
                )

        self.hla_antibodies_per_groups = split_antibodies_to_groups(hla_antibodies_over_cutoff_list)


@dataclass
class PatientParameters:
    blood_group: BloodGroup
    country_code: Country
    hla_typing: HLATyping
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None


def split_hla_types_to_groups(hla_types: List[HLAType]) -> List[HLAPerGroup]:
    hla_types_in_groups = dict()
    for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_types:
        match_found = False
        for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
            if re.match(HLA_GROUP_SPLIT_CODE_REGEX[hla_group], hla_type.code):
                hla_types_in_groups[hla_group].append(hla_type)
                match_found = True
                break
        if not match_found:
            raise AssertionError(f'Unexpected hla_code: {hla_type.code}')
    return [HLAPerGroup(hla_group, hla_codes_in_group) for hla_group, hla_codes_in_group in
            hla_types_in_groups.items()]


# TODO: share logic with split_hla_types_to_groups
def split_antibodies_to_groups(hla_antibodies: List[HLAAntibody]) -> List[AntibodiesPerGroup]:
    hla_types_in_groups = dict()
    for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_antibodies:
        match_found = False
        for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
            if re.match(HLA_GROUP_SPLIT_CODE_REGEX[hla_group], hla_type.code):
                hla_types_in_groups[hla_group].append(hla_type)
                match_found = True
                break
        if not match_found:
            raise AssertionError(f'Unexpected hla_code: {hla_type.code}')
    return [AntibodiesPerGroup(hla_group, hla_codes_in_group) for hla_group, hla_codes_in_group in
            hla_types_in_groups.items()]
