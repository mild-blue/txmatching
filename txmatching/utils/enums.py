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


# pylint:disable=invalid-name
class HLAGroup(str, Enum):
    A = 'A'
    B = 'B'
    DRB1 = 'DRB1'
    CW = 'CW'
    DP = 'DP'
    DQ = 'DQ'
    OTHER_DR = 'OTHER_DR'
    INVALID_CODES = 'INVALID_CODES'
    ALL = 'ALL'


class DQDPChain(str, Enum):
    ALPHA_DQ = 'DQA'
    BETA_DQ = 'DQB'
    ALPHA_DP = 'DPA'
    BETA_DP = 'DPB'


class Scorer(str, Enum):
    SplitScorer = 'SplitScorer'
    HighResScorer = 'HighResScorer'
    HighResWithDQDPScorer = 'HighResWithDQDPScorer'


class Solver(str, Enum):
    AllSolutionsSolver = 'AllSolutionsSolver'
    ILPSolver = 'ILPSolver'


class StrictnessType(str, Enum):
    """
    Enum representing the strictness of HLA parsing.
    Strict = normal parsing, no exceptions being made.
    Forgiving = some parsing errors and warnings are overlooked for the sake of including recipients in a matching.
    """
    STRICT = 'STRICT'
    FORGIVING = 'FORGIVING'


# pylint:enable=invalid-name

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
        split_code_regex=r'(^DPA\d+)|(^DP\d+)',
        high_res_code_regex=r'(DPA1\*)|(DPB1\*)',
        max_count_per_patient=4
    ),
    HLAGroup.DQ: HLAGroupProperties(
        name='DQ',
        split_code_regex=r'(^DQA\d+)|(^DQ\d+)',
        high_res_code_regex=r'(DQA1\*)|(DQB1\*)',
        max_count_per_patient=4
    ),
    # Based on email communication with Matej Roder from 12.5.2020:
    # Each DRB3,4,5 (DR51,52,53 in split) can have 0 to 2 genes for DRB3, 0 to 2 genes for DRB, and 0 to 2 genes for
    # DRB5. But, there can be only 0 to 2 genes from DRB3,4,5 in total. E.g. there can't be a person with DRB3, DRB4,
    # DRB5 at the same time, because that would mean they have 3 genes from this group in total, which is not possible
    # (at least not found in anybody till now).
    HLAGroup.OTHER_DR: HLAGroupProperties(
        name='OTHER_DR',
        split_code_regex=r'^DR5[123]',
        high_res_code_regex=r'DRB[^1]\*',
        max_count_per_patient=2
    )
}

HLA_GROUPS_OTHER = [HLAGroup.CW, HLAGroup.DP, HLAGroup.DQ, HLAGroup.OTHER_DR]
GENE_HLA_GROUPS = [HLAGroup.A, HLAGroup.B, HLAGroup.DRB1]
SPECIAL_HLA_GROUPS = [HLAGroup.OTHER_DR, HLAGroup.INVALID_CODES]
HLA_GROUPS = GENE_HLA_GROUPS + HLA_GROUPS_OTHER
assert set(HLA_GROUPS_OTHER + GENE_HLA_GROUPS + SPECIAL_HLA_GROUPS + [HLAGroup.ALL]) == set(HLAGroup)


def _combine_properties_of_groups(group_list: List[HLAGroup]) -> HLAGroupProperties:
    return HLAGroupProperties(
        HLAGroup.ALL.name,
        '(' + ')|('.join([HLA_GROUPS_PROPERTIES[hla_group].split_code_regex for hla_group in group_list]) + ')',
        '(' + ')|('.join([HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex for hla_group in group_list]) + ')',
        sum(HLA_GROUPS_PROPERTIES[hla_group].max_count_per_patient for hla_group in group_list)
    )


HLA_GROUPS_PROPERTIES[HLAGroup.ALL] = _combine_properties_of_groups(HLA_GROUPS)


# BW group is not here can be ignored as the information is redundant see http://hla.alleles.org/antigens/bw46.html
# It is based on our discussions with immunologists, therefore it is not even in this list

class HLAAntibodyType(str, Enum):
    NORMAL = 'NORMAL'
    THEORETICAL = 'THEORETICAL'


class HLACrossmatchLevel(str, Enum):
    NONE = 'NONE'  # nothing is allowed
    BROAD = 'BROAD'
    SPLIT_AND_BROAD = 'SPLIT_AND_BROAD'


class AntibodyMatchTypes(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'
    # when we have antibodies for a group that patient doesn't have typization for
    UNDECIDABLE = 'UNDECIDABLE'
    HIGH_RES_WITH_SPLIT = 'HIGH_RES_WITH_SPLIT'
    HIGH_RES_WITH_BROAD = 'HIGH_RES_WITH_BROAD'
    THEORETICAL = 'THEORETICAL'

    def is_positive_for_level(self, crossmatch_level: HLACrossmatchLevel) -> bool:
        return (
                crossmatch_level == HLACrossmatchLevel.NONE and
                self in [self.BROAD, self.SPLIT, self.HIGH_RES, self.HIGH_RES_WITH_SPLIT, self.HIGH_RES_WITH_BROAD] or
                crossmatch_level == HLACrossmatchLevel.BROAD and self in [self.BROAD, self.SPLIT, self.HIGH_RES,
                                                                          self.HIGH_RES_WITH_SPLIT] or
                crossmatch_level == HLACrossmatchLevel.SPLIT_AND_BROAD and self in [self.BROAD, self.HIGH_RES,
                                                                                    self.SPLIT]
        )


class MatchType(str, Enum):
    SPLIT = 'SPLIT'
    BROAD = 'BROAD'
    HIGH_RES = 'HIGH_RES'
    NONE = 'NONE'


class TxmEventState(str, Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
