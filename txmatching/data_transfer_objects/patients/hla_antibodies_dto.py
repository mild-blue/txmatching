from dataclasses import dataclass, field
from typing import List

from txmatching.auth.exceptions import InvalidArgumentException


@dataclass
class HLAAntibodyDTO:
    raw_code: str
    mfi: int

    def __post_init__(self):
        if self.mfi < 0:
            raise InvalidArgumentException("MFI cannot be negative")


@dataclass
class HLAAntibodiesDTO:
    hla_antibodies_list: List[HLAAntibodyDTO] = field(default_factory=list)
