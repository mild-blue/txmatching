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
            is_id_valid(self.id)


def is_id_valid(id: int):
    if id < 0:
        raise ValueError("Invalid id, it must be greater than 0")

