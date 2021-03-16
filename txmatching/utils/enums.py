from enum import Enum


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

HLA_GROUP_CODE_REGEX = {
    HLAGroup.A: r'^A\*?\d+',
    HLAGroup.B: r'^B\*?\d+',
    HLAGroup.CW: r'CW\d+',
    HLAGroup.DRB1: r'DR(?!5([123]))',
    HLAGroup.DP: r'DPA?\d+',
    HLAGroup.DQ: r'DQA?\d+',
    HLAGroup.OTHER_DR: r'DR5[123]',
    HLAGroup.BW: r'BW\d+',
    HLAGroup.Other: r'.*'
}


class AntibodyMatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'


class MatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'
