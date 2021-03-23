from dataclasses import dataclass
from enum import Enum
from typing import List


class Sex(str, Enum):
    M = 'M'
    F = 'F'


@dataclass
class HLAGroupProperties:
    name: str
    split_code_regex: str
    high_res_code_regex: str
    max_count_per_patient: int


class HLAGroup(str, Enum):
    A = 'A'
    B = 'B'
    DRB1 = 'DRB1'
    CW = 'CW'
    DP = 'DP'
    DQ = 'DQ'
    OTHER_DR = 'OTHER_DR'
    Other = 'Other'
    ALL = 'ALL'


HLA_GROUPS_PROPERTIES = {
    HLAGroup.A: HLAGroupProperties(
        'A',
        r'^A\d+',
        r'^A\*',
        2
    ),
    HLAGroup.B: HLAGroupProperties(
        'A',
        r'^B\d+',
        r'^B\*',
        2
    ),
    HLAGroup.DRB1: HLAGroupProperties(
        'A',
        r'^DR(?!5([123]))\d',
        r'DRB1\*',
        2
    ),
    HLAGroup.CW: HLAGroupProperties(
        'A',
        r'^CW\d+',
        r'^C\*',
        2
    ),
    HLAGroup.DP: HLAGroupProperties(
        'A',
        r'^DPA?\d+',
        r'DP[AB]1\*',
        4
    ),
    HLAGroup.DQ: HLAGroupProperties(
        'A',
        r'^DQA?\d+',
        r'DQ[AB]1\*',
        4
    ),
    HLAGroup.OTHER_DR: HLAGroupProperties(
        'OTHER_DR',
        r'^DR5[123]',
        r'DRB[^1]\*',
        2  # TODO check if this is correct https://github.com/mild-blue/txmatching/issues/592
    )
}

HLA_GROUPS_OTHER = [HLAGroup.CW, HLAGroup.DP, HLAGroup.DQ, HLAGroup.OTHER_DR]
GENE_HLA_GROUPS = [HLAGroup.A, HLAGroup.B, HLAGroup.DRB1]
GENE_HLA_GROUPS_WITH_OTHER = [group for group in GENE_HLA_GROUPS] + [HLAGroup.Other]
assert set(HLA_GROUPS_OTHER + GENE_HLA_GROUPS + [HLAGroup.Other, HLAGroup.ALL]) == set(HLAGroup)


def _combine_properties_of_groups(group_list: List[HLAGroup]) -> HLAGroupProperties:
    return HLAGroupProperties(
        HLAGroup.Other.name,
        '(' + ')|('.join([HLA_GROUPS_PROPERTIES[hla_group].split_code_regex for hla_group in group_list]) + ')',
        '(' + ')|('.join([HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex for hla_group in group_list]) + ')',
        sum([HLA_GROUPS_PROPERTIES[hla_group].max_count_per_patient for hla_group in group_list])
    )


HLA_GROUPS_PROPERTIES[HLAGroup.Other] = _combine_properties_of_groups(HLA_GROUPS_OTHER)
HLA_GROUPS_PROPERTIES[HLAGroup.ALL] = _combine_properties_of_groups(GENE_HLA_GROUPS_WITH_OTHER)


# BW group is not here can be ignored as the information is redundant see http://hla.alleles.org/antigens/bw46.html
# It is based on our discussions with immunologists, therefore it is not even in this list


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


class MatchType(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'
