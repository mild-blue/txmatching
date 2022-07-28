from dataclasses import dataclass


@dataclass
class SuccessDTOOut:
    success: bool

# pylint:enable=invalid-name
@dataclass
class IdentifierDTOIn:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name

    def __post_init__(self):
        if self.id:
            if self.id < 0:
                raise ValueError(f"Invalid id with value {self.id} it must be greater than 0")
