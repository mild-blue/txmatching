from dataclasses import dataclass, field
from typing import List


@dataclass
class HLATypeUpdateDTO:
    raw_code: str


@dataclass
class HLATypingUpdateDTO:
    hla_types_list: List[HLATypeUpdateDTO] = field(default_factory=list)
