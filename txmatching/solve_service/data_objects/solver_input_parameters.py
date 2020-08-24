from dataclasses import dataclass
from typing import List

from txmatching.config.configuration import Configuration
from txmatching.patients.donor import Donor
from txmatching.patients.recipient import Recipient


@dataclass
class SolverInputParameters:
    donors: List[Donor]
    recipients: List[Recipient]
    configuration: Configuration
