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

HLA_GROUP_SPLIT_CODE_REGEX = {
    HLAGroup.A: r'^A\d+',
    HLAGroup.B: r'^B\d+',
    HLAGroup.CW: r'^CW\d+',
    HLAGroup.DRB1: r'^DR(?!5([123]))\d',
    HLAGroup.DP: r'^DPA?\d+',
    HLAGroup.DQ: r'^DQA?\d+',
    HLAGroup.OTHER_DR: r'^DR5[123]',
    HLAGroup.BW: r'^BW\d+',
    HLAGroup.Other: r'.*'
}

HLA_GROUP_HIGH_RES_CODE_REGEX = {
    HLAGroup.A: r'^A\*',
    HLAGroup.B: r'^B\*',
    HLAGroup.CW: r'C\*',
    HLAGroup.DRB1: r'DRB1\*',
    HLAGroup.DP: r'DPA1\*',
    HLAGroup.DQ: r'DQA1\*',
    HLAGroup.OTHER_DR: r'DRB[^1]\*',
    HLAGroup.BW: r'BW\*',
    HLAGroup.Other: r'.*'
}


class HLACrossmatchLevel(str, Enum):
    BROAD_AND_HIGHER = 'BROAD_AND_HIGHER'
    SPLIT_AND_HIGHER = 'SPLIT_AND_HIGHER'
    HIGH_RES = 'HIGH_RES'


class AntibodyMatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'

    def is_positive_for_level(self, crossmatch_level: HLACrossmatchLevel) -> bool:
        return (
                crossmatch_level == HLACrossmatchLevel.BROAD_AND_HIGHER and
                self in [self.BROAD, self.SPLIT, self.HIGH_RES] or
                crossmatch_level == HLACrossmatchLevel.SPLIT_AND_HIGHER and self in [self.SPLIT, self.HIGH_RES] or
                crossmatch_level == HLACrossmatchLevel.HIGH_RES and self == self.HIGH_RES
        )


class MatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'
