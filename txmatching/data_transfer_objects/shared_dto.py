from dataclasses import dataclass
from txmatching.configuration.configuration import does_configuration_exist


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
        does_configuration_exist(self.id)
