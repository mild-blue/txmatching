from dataclasses import dataclass
from typing import List

from kidney_exchange.patients.patient_types import CountryCode, MedicalId


@dataclass
class Transplant:
    score: int
    donor: MedicalId
    recipient: MedicalId


@dataclass
class RoundDTO:
    transplants: List[Transplant]


class CountryDTO:
    country_code: CountryCode
    donor_count: int
    recipient_count: int


@dataclass
class MatchingDTO:
    score: int
    rounds: List[RoundDTO]
    countries: List[CountryDTO]
