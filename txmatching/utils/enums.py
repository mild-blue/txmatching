from enum import Enum


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
    BW = 'BW'
    OTHER_DR = 'OTHER_DR'
    Other = 'Other'


HLA_GROUPS_GENE = [HLAGroup.A, HLAGroup.B, HLAGroup.DRB1]
HLA_GROUPS_OTHER = [HLAGroup.CW, HLAGroup.DP, HLAGroup.DQ, HLAGroup.OTHER_DR, HLAGroup.BW]
HLA_GROUPS_NAMES_WITH_OTHER = [group for group in HLA_GROUPS_GENE] + [HLAGroup.Other]

HLA_GROUP_SPLIT_CODE_REGEX = {
    HLAGroup.A: r'^A\d+',
    HLAGroup.B: r'^B\d+',
    HLAGroup.CW: r'CW\d+',
    HLAGroup.DRB1: r'DR(?!5([123]))',
    HLAGroup.DP: r'DPA?\d+',
    HLAGroup.DQ: r'DQA?\d+',
    HLAGroup.OTHER_DR: r'DR5[123]',
    HLAGroup.BW: r'BW\d+'
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
