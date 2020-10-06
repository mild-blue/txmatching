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


class BloodGroup(str, Enum):
    A = 'A'
    B = 'B'
    AB = 'AB'
    ZERO = '0'

    @classmethod
    def _missing_(cls, name):
        if name == 0:
            return cls.ZERO
        raise ValueError(f'{name} is not a valid BloodGroup')
