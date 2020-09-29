from enum import Enum


class Country(str, Enum):
    CZE = 'CZE'
    IL = 'IL'
    AUT = 'AUT'


class Sex(str, Enum):
    M = 'M'
    F = 'F'
