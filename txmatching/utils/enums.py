import re
from enum import Enum
from typing import List, Dict


class Country(str, Enum):
    CZE = 'CZE'
    ISR = 'ISR'
    AUT = 'AUT'
    CAN = 'CAN'
    IND = 'IND'


class Sex(str, Enum):
    M = 'M'
    F = 'F'


class HLAGroups(str, Enum):
    A = 'A'
    B = 'B'
    DRB1 = 'DRB1'
    CW = 'CW'
    DP = 'DP'
    DQ = 'DQ'
    OTHER_DR = 'OTHER_DR'


HLA_GROUP_SPLIT_CODE_REGEX = {
    HLAGroups.A: re.compile(r'^A\d*'),
    HLAGroups.B: re.compile(r'^B\d*'),
    HLAGroups.CW: re.compile(r'CW\d*'),
    HLAGroups.DRB1: re.compile(r'DR(?!5([123]))'),
    HLAGroups.DP: re.compile(r'DP\d*'),
    HLAGroups.DQ: re.compile(r'DQ\d*'),
    HLAGroups.OTHER_DR: re.compile(r'DR5[123]')
}

HLA_GROUPS_GENE = [HLAGroups.A, HLAGroups.B, HLAGroups.DRB1]
HLA_OTHER_GROUPS_NAME = 'Other'
HLA_GROUPS_OTHER = [HLAGroups.CW, HLAGroups.DP, HLAGroups.DQ, HLAGroups.OTHER_DR]

HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS = {
    HLAGroups.A: 1.0,
    HLAGroups.B: 3.0,
    HLAGroups.DRB1: 9.0,
}


class MatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'


MATCH_TYPE_BONUS = {
    MatchTypes.BROAD: 1,
    MatchTypes.SPLIT: 1,
    MatchTypes.HIGH_RES: 1
}


def split_to_hla_groups(hla_codes: List[str]) -> Dict[str, List[str]]:
    hla_codes_in_groups = dict()
    for hla_group in HLA_GROUPS_GENE:
        hla_codes_in_groups[hla_group.name] = []
    hla_codes_in_groups[HLA_OTHER_GROUPS_NAME] = []
    for hla_code in hla_codes:
        match_found = False
        for hla_group in HLA_GROUPS_GENE:
            if re.match(HLA_GROUP_SPLIT_CODE_REGEX[hla_group], hla_code):
                hla_codes_in_groups[hla_group.name] += [hla_code]
                match_found = True
                break
        if not match_found:
            hla_codes_in_groups[HLA_OTHER_GROUPS_NAME] += [hla_code]
    return hla_codes_in_groups
