from dataclasses import dataclass
from typing import List

from txmatching.config.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient


@dataclass
class SolverInputParameters:
    donors: List[Donor]
    recipients: List[Recipient]
    configuration: Configuration
