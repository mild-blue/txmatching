from dataclasses import dataclass


@dataclass
class TxmEventDTOIn:
    name: str


@dataclass
class TxmDefaultEventDTOIn:
    id: int
