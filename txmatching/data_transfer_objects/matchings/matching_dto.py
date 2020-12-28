from dataclasses import dataclass
from typing import List, Set

from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import MedicalId
from txmatching.utils.enums import Country, HLAGroups, AntibodyMatchTypes
# pylint: disable=too-many-instance-attributes
from txmatching.utils.hla_system.compatibility_index import \
    DetailedCompatibilityIndexForHLAGroup
from txmatching.utils.hla_system.hla_crossmatch import AntibodyMatchForHLAGroup


@dataclass
class TransplantDTOOut:
    score: float
    compatible_blood: bool
    donor: MedicalId
    recipient: MedicalId
    detailed_compatibility_index: List[DetailedCompatibilityIndexForHLAGroup]
    detailed_antibody_matches: List[AntibodyMatchForHLAGroup]


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
class TransplantDTO:
    score: float
    compatible_blood: bool
    donor: Donor
    recipient: Recipient


@dataclass
class RoundReportDTO:
    transplants: List[TransplantDTO]


@dataclass
class MatchingReportDTO:
    score: float
    rounds: List[RoundReportDTO]
    countries: List[CountryDTO]
    order_id: int
    count_of_transplants: int
