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


class HLATypes(Enum):
    A = 'A'
    B = 'B'
    DR = 'DR'


ANTIBODIES_MULTIPLIERS = {
    HLATypes.A: 1,
    HLATypes.B: 2,
    HLATypes.DR: 9
}

ANTIBODIES_MULTIPLIERS_STR = {
    HLATypes.A.value: 1,
    HLATypes.B.value: 2,
    HLATypes.DR.value: 9
}
