from dataclasses import dataclass, field
from typing import List

from txmatching.patients.patient_parameters import HLAAntibody


@dataclass
class HLAAntibodiesDTO:
    hla_antibodies_list: List[HLAAntibody] = field(default_factory=list)
