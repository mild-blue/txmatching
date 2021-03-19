from dataclasses import dataclass


@dataclass
class SuccessDTOOut:
    success: bool


@dataclass
class IdentifierDTOIn:
    id: int
