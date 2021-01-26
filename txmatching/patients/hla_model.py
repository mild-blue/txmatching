import itertools
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from txmatching.utils.enums import (HLA_GROUP_SPLIT_CODE_REGEX,
                                    HLA_GROUPS_NAMES_WITH_OTHER, HLAGroup)
from txmatching.utils.hla_system.hla_transformations import (
    get_mfi_from_multiple_hla_codes, parse_hla_raw_code)
from txmatching.utils.logging_tools import PatientAdapter


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
        return isinstance(other, HLAType) and self.raw_code == other.raw_code

    def __hash__(self):
        return hash(self.raw_code)


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
            self.hla_per_groups = _split_hla_types_to_groups(hla_types)


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
                self.raw_code == other.raw_code and
                self.mfi == other.mfi and
                self.cutoff == other.cutoff)

    def __hash__(self):
        return hash((self.raw_code, self.mfi, self.cutoff))


@dataclass
class AntibodiesPerGroup:
    hla_group: HLAGroup
    hla_antibody_list: List[HLAAntibody]


@dataclass
class HLAAntibodies:
    hla_antibodies_list: List[HLAAntibody] = field(default_factory=list)
    hla_antibodies_per_groups: List[AntibodiesPerGroup] = field(default_factory=list)

    def __init__(self, hla_antibodies_list: List[HLAAntibody] = None,
                 logger_with_patient: Union[logging.Logger, PatientAdapter] = logging.getLogger(__name__)):
        if hla_antibodies_list is None:
            hla_antibodies_list = []
        self.hla_antibodies_list = hla_antibodies_list
        hla_antibodies_list_without_none = [hla_antibody for hla_antibody in hla_antibodies_list if hla_antibody.code]
        grouped_hla_antibodies = itertools.groupby(
            sorted(hla_antibodies_list_without_none,
                   key=lambda hla_antibody: (hla_antibody.code, hla_antibody.cutoff, hla_antibody.raw_code)),
            key=lambda hla_antibody: (hla_antibody.code, hla_antibody.cutoff, hla_antibody.raw_code)
        )
        hla_antibodies_over_cutoff_list = []
        for (hla_code, hla_code_cutoff, hla_code_raw), antibody_group in grouped_hla_antibodies:
            antibody_group_list = list(antibody_group)
            assert len(antibody_group_list) > 0
            mfi = get_mfi_from_multiple_hla_codes([hla_code.mfi for hla_code in antibody_group_list],
                                                  hla_code_cutoff,
                                                  hla_code_raw,
                                                  logger_with_patient)
            if mfi >= hla_code_cutoff:
                new_antibody = HLAAntibody(
                    code=hla_code,
                    raw_code=hla_code_raw,
                    cutoff=hla_code_cutoff,
                    mfi=mfi
                )
                hla_antibodies_over_cutoff_list.append(new_antibody)

        self.hla_antibodies_per_groups = _split_antibodies_to_groups(hla_antibodies_over_cutoff_list)


def _split_hla_types_to_groups(hla_types: List[HLAType]) -> List[HLAPerGroup]:
    hla_types_in_groups = _split_hla_codes_to_groups(hla_types)
    return [HLAPerGroup(hla_group,
                        sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                        ) for hla_group, hla_codes_in_group in
            hla_types_in_groups.items()]


# Beware this code is similar to code in function split_hla_types_to_groups,
# if you are chaning this code it is likely you want to change the other function as well.
# Ideally when doing so, try to share the logic between the functions.
def _split_antibodies_to_groups(hla_antibodies: List[HLAAntibody]) -> List[AntibodiesPerGroup]:
    hla_antibodies_in_groups = _split_hla_codes_to_groups(hla_antibodies)
    return [AntibodiesPerGroup(hla_group,
                               sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                               ) for hla_group, hla_codes_in_group in
            hla_antibodies_in_groups.items()]


HLACodeAlias = Union[HLAType, HLAAntibody]


def _split_hla_codes_to_groups(hla_codes: List[HLACodeAlias]
                               ) -> Dict[HLAGroup, List[HLACodeAlias]]:
    hla_types_in_groups = dict()
    for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_codes:
        match_found = False
        for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
            if re.match(HLA_GROUP_SPLIT_CODE_REGEX[hla_group], hla_type.code):
                hla_types_in_groups[hla_group].append(hla_type)
                match_found = True
                break
        if not match_found:
            raise AssertionError(f'Unexpected hla_code: {hla_type.code}')
    return hla_types_in_groups
