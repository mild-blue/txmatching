from dataclasses import dataclass
from typing import Optional

from txmatching.utils.enums import TxmEventState


@dataclass
class TxmEventDTOIn:
    name: str


@dataclass
class TxmDefaultEventDTOIn:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name


@dataclass
class TxmEventUpdateDTOIn:
    state: Optional[TxmEventState]
