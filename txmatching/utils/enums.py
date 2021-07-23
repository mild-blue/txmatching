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


class Scorer(str, Enum):
    SplitScorer = 'SplitScorer'
    HighResScorer = 'HighResScorer'
    HighResWithDQDPScorer = 'HighResWithDQDPScorer'


class Solver(str, Enum):
    AllSolutionsSolver = 'AllSolutionsSolver'
    ILPSolver = 'ILPSolver'


HLA_GROUPS_PROPERTIES = {
    HLAGroup.A: HLAGroupProperties(
        name='A',
        split_code_regex=r'^A\d+',
        high_res_code_regex=r'^A\*',
        max_count_per_patient=2
    ),
    HLAGroup.B: HLAGroupProperties(
        name='B',
        split_code_regex=r'^B\d+',
        high_res_code_regex=r'^B\*',
        max_count_per_patient=2
    ),
    HLAGroup.DRB1: HLAGroupProperties(
        name='DRB1',
        split_code_regex=r'^DR(?!5([123]))\d',
        high_res_code_regex=r'DRB1\*',
        max_count_per_patient=2
    ),
    HLAGroup.CW: HLAGroupProperties(
        name='CW',
        split_code_regex=r'^CW\d+',
        high_res_code_regex=r'^C\*',
        max_count_per_patient=2
    ),
    HLAGroup.DP: HLAGroupProperties(
        name='DP',
        split_code_regex=r'^DPA?\d+',
        high_res_code_regex=r'DP[AB]1\*',
        max_count_per_patient=4
    ),
    HLAGroup.DQ: HLAGroupProperties(
        name='DQ',
        split_code_regex=r'^DQA?\d+',
        high_res_code_regex=r'DQ[AB]1\*',
        max_count_per_patient=4
    ),
    HLAGroup.OTHER_DR: HLAGroupProperties(
        name='OTHER_DR',
        split_code_regex=r'^DR5[123]',
        high_res_code_regex=r'DRB[^1]\*',
        max_count_per_patient=2  # TODO check if this is correct https://github.com/mild-blue/txmatching/issues/592
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
    NONE = 'NONE'  # nothing is allowed
    BROAD = 'BROAD'
    SPLIT_AND_BROAD = 'SPLIT_AND_BROAD'


class AntibodyMatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'

    def is_positive_for_level(self, crossmatch_level: HLACrossmatchLevel) -> bool:
        return (
                crossmatch_level == HLACrossmatchLevel.NONE and
                self in [self.BROAD, self.SPLIT, self.HIGH_RES] or
                crossmatch_level == HLACrossmatchLevel.BROAD and self in [self.SPLIT, self.HIGH_RES] or
                crossmatch_level == HLACrossmatchLevel.SPLIT_AND_BROAD and self == self.HIGH_RES
        )


class MatchType(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'


class TxmEventState(str, Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
