from dataclasses import dataclass
from datetime import date
from typing import Optional

from txmatching.auth.exceptions import InvalidArgumentException

Kilograms = float
Centimeters = int
THIS_YEAR = date.today().year


@dataclass(kw_only=True)
class PatientBaseDTO:
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None

    def __post_init__(self):
        if self.weight:
            _is_weight_valid(self.weight)
        if self.height:
            _is_height_valid(self.height)
        if self.year_of_birth:
            _is_year_of_birth_valid(self.year_of_birth)


def _is_height_valid(height: Centimeters):
    if height < 0:
        raise InvalidArgumentException(f'Invalid patient height {height}cm.')


def _is_weight_valid(weight: Kilograms):
    if weight < 0:
        raise InvalidArgumentException(f'Invalid patient weight {weight}kg.')


def _is_year_of_birth_valid(year_of_birth: Centimeters):
    if year_of_birth < 1900 or year_of_birth > THIS_YEAR:
        raise InvalidArgumentException(f'Invalid patient year of birth {year_of_birth}')


@dataclass(kw_only=True)
class RecipientBaseDTO:
    previous_transplants: Optional[int] = None

    def __post_init__(self):
        if self.previous_transplants and self.previous_transplants < 0:
            raise InvalidArgumentException(
                f'Invalid recipient number of previous transplants {self.previous_transplants}.')
