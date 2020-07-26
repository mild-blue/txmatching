from dataclasses import dataclass
from typing import List

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient


@dataclass
class SolverInputParameters:
    donors: List[Donor]
    recipients: List[Recipient]
    configuration: Configuration
