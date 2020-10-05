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
