from dataclasses import dataclass, field
from typing import List


@dataclass
class HLAAntibodyDTO:
    raw_code: str
    mfi: int


@dataclass
class HLAAntibodiesDTO:
    hla_antibodies_list: List[HLAAntibodyDTO] = field(default_factory=list)
