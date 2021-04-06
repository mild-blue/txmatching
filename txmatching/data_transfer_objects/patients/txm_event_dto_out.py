from dataclasses import dataclass
from typing import List, Optional

from txmatching.utils.enums import TxmEventState


@dataclass
class TxmEventDTOOut:
    id: int
    name: str
    default_config_id: Optional[int]
    state: TxmEventState


@dataclass
class TxmEventsDTOOut:
    events: List[TxmEventDTOOut]
