from dataclasses import dataclass
from typing import Optional

from txmatching.utils.enums import TxmEventState


@dataclass
class TxmEventDTOIn:
    name: str


@dataclass
class TxmDefaultEventDTOIn:
    id: int


@dataclass
class TxmEventUpdateDTOIn:
    state: Optional[TxmEventState]
