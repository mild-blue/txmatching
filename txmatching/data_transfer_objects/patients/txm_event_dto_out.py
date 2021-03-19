from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TxmEventDTOOut:
    id: int
    name: str
    default_config_id: Optional[int]


@dataclass
class TxmEventsDTOOut:
    events: List[TxmEventDTOOut]
