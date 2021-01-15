import re
from dataclasses import dataclass
from enum import Enum
from typing import List

from txmatching.patients.patient_parameters_dataclasses import HLAType


class Country(str, Enum):
    CZE = 'CZE'
    ISR = 'ISR'
    AUT = 'AUT'
    CAN = 'CAN'
    IND = 'IND'


class Sex(str, Enum):
    M = 'M'
    F = 'F'


class HLAGroup(str, Enum):
    A = 'A'
    B = 'B'
    DRB1 = 'DRB1'
    CW = 'CW'
    DP = 'DP'
    DQ = 'DQ'
    OTHER_DR = 'OTHER_DR'
    Other = 'Other'


HLA_GROUPS_GENE = [HLAGroup.A, HLAGroup.B, HLAGroup.DRB1]
HLA_GROUPS_OTHER = [HLAGroup.CW, HLAGroup.DP, HLAGroup.DQ, HLAGroup.OTHER_DR]
HLA_GROUPS_NAMES_WITH_OTHER = [group for group in HLA_GROUPS_GENE] + [HLAGroup.Other]

HLA_GROUP_SPLIT_CODE_REGEX = {
    HLAGroup.A: r'^A\d*',
    HLAGroup.B: r'^B\d*',
    HLAGroup.CW: r'CW\d*',
    HLAGroup.DRB1: r'DR(?!5([123]))',
    HLAGroup.DP: r'DP\d*',
    HLAGroup.DQ: r'DQ\d*',
    HLAGroup.OTHER_DR: r'DR5[123]'
}

HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.Other] = '|'.join(
    HLA_GROUP_SPLIT_CODE_REGEX[hla_group] for hla_group in HLA_GROUPS_OTHER)

HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS = {
    HLAGroup.A: 1.0,
    HLAGroup.B: 3.0,
    HLAGroup.DRB1: 9.0,
    HLAGroup.Other: 0.0
}


class AntibodyMatchTypes(str, Enum):
    NONE = 'NONE'
    MATCH = 'MATCH'


class MatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'


MATCH_TYPE_BONUS = {
    MatchTypes.BROAD: 1,
    MatchTypes.SPLIT: 1,
    MatchTypes.HIGH_RES: 1
}


# TODOO: move from enums
@dataclass
class CodesPerGroup:
    hla_group: HLAGroup
    hla_codes: List[HLAType]  # TODOO: rename


def split_to_hla_groups(hla_types: List[HLAType]) -> List[CodesPerGroup]:
    hla_codes_in_groups = dict()
    for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
        hla_codes_in_groups[hla_group] = []
    for hla_type in hla_types:
        match_found = False
        for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
            if re.match(HLA_GROUP_SPLIT_CODE_REGEX[hla_group], hla_type.code):  # TODOO
                hla_codes_in_groups[hla_group] += [hla_type]
                match_found = True
                break
        if not match_found:
            raise AssertionError(f'Unexpected hla_code: {hla_type.code}')
    return [CodesPerGroup(hla_group, hla_codes_in_group) for hla_group, hla_codes_in_group in
            hla_codes_in_groups.items()]
