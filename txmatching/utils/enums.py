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
    DPA = 'DPA'
    DPB = 'DPB'
    DQA = 'DQA'
    DQB = 'DQB'
    OTHER_DR = 'OTHER_DR'
    INVALID_CODES = 'INVALID_CODES'
    ALL = 'ALL'


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
    HLAGroup.DPA: HLAGroupProperties(
        name='DPA',
        split_code_regex=r'^DPA\d+',
        high_res_code_regex=r'DPA1\*',
        max_count_per_patient=4
    ),
    HLAGroup.DPB: HLAGroupProperties(
        name='DPB',
        split_code_regex=r'^DP\d+',
        high_res_code_regex=r'DPB1\*',
        max_count_per_patient=4
    ),
    HLAGroup.DQA: HLAGroupProperties(
        name='DQA',
        split_code_regex=r'^DQA\d+',
        high_res_code_regex=r'DQA1\*',
        max_count_per_patient=4
    ),
    HLAGroup.DQB: HLAGroupProperties(
        name='DQB',
        split_code_regex=r'^DQ\d+',
        high_res_code_regex=r'DQB1\*',
        max_count_per_patient=4
    ),
    # Na zaklade emailu od Mateje Rodera z 12.5.2020:
    # U DRB3,4,5 (dr51,52,53 ve split) je to tak, že každý může mít 0 až 2 geny pro DRB3, 0 až 2 geny pro DRB4 a 0 až 2
    # geny pro DRB5. Zároveň však platí, že může mít pouze 0 až 2 jakékoliv geny DRB345. Čili neexistuje jedinec, který
    # by měl například 1 funkční protein DRB3, DRB4 i DRB5, protože pak by jich měl dohromady 3, což není možné, rsp.
    # to zatím u žádného člověka nebylo objeveno.
    HLAGroup.OTHER_DR: HLAGroupProperties(
        name='OTHER_DR',
        split_code_regex=r'^DR5[123]',
        high_res_code_regex=r'DRB[^1]\*',
        max_count_per_patient=2
    )
}

HLA_GROUPS_OTHER = [HLAGroup.CW, HLAGroup.DPA, HLAGroup.DPB, HLAGroup.DQA, HLAGroup.DQB, HLAGroup.OTHER_DR]
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
