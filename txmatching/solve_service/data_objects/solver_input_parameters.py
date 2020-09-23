from dataclasses import dataclass

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import TxmEvent


@dataclass
class SolverInputParameters:
    txm_event: TxmEvent
    configuration: Configuration
