from dataclasses import dataclass
from typing import List


@dataclass
class TxmEventDTOOut:
    id: int
    name: str


@dataclass
class TxmEventsDTOOut:
    events: List[TxmEventDTOOut]
