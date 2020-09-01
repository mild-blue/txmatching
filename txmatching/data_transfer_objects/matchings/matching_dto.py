from dataclasses import dataclass
from typing import List

from txmatching.patients.patient_types import CountryCode, MedicalId


@dataclass
class Transplant:
    score: float
    compatible_blood: bool
    donor: MedicalId
    recipient: MedicalId


@dataclass
class RoundDTO:
    transplants: List[Transplant]


@dataclass
class CountryDTO:
    country_code: CountryCode
    donor_count: int
    recipient_count: int


@dataclass
class MatchingDTO:
    score: float
    rounds: List[RoundDTO]
    countries: List[CountryDTO]
