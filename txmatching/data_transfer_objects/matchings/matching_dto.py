from dataclasses import dataclass
from typing import List, Optional

from txmatching.patients.patient_types import MedicalId
from txmatching.utils.country_enum import Country
# pylint: disable=too-many-instance-attributes
from txmatching.utils.hla_system.detailed_score import DetailedScoreForHLAGroup
from txmatching.utils.transplantation_warning import TransplantWarnings


@dataclass
class TransplantDTOOut:
    score: float
    max_score: float
    compatible_blood: bool
    donor: MedicalId
    recipient: MedicalId
    detailed_score_per_group: List[DetailedScoreForHLAGroup]
    transplant_messages: Optional[TransplantWarnings] = None


@dataclass
class RoundDTO:
    transplants: List[TransplantDTOOut]


@dataclass
class CountryDTO:
    country_code: Country
    donor_count: int
    recipient_count: int


@dataclass
class MatchingDTO:
    score: float
    rounds: List[RoundDTO]
    countries: List[CountryDTO]
    order_id: int
    count_of_transplants: int


@dataclass
class CalculatedMatchingsDTO:
    calculated_matchings: List[MatchingDTO]
    number_of_possible_transplants: Optional[int]
    number_of_possible_recipients: Optional[int]
    config_id: int
