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


class HLATypes(str, Enum):
    A = 'A'
    B = 'B'
    DR = 'DR'


HLA_TYPING_BONUS_PER_GENE_CODE = {
    HLATypes.A: 1,
    HLATypes.B: 3,
    HLATypes.DR: 9
}

HLA_TYPING_BONUS_PER_GENE_CODE_STR = {
    HLATypes.A.value: 1,
    HLATypes.B.value: 3,
    HLATypes.DR.value: 9
}
