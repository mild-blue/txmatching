from dataclasses import dataclass
from typing import Dict

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import RecipientDbId, DonorDbId


@dataclass
class SolverInputParameters:
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    configuration: Configuration
