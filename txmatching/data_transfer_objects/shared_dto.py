from dataclasses import dataclass
from txmatching.configuration.configuration import raise_error_if_configuration_does_not_exist


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
        raise_error_if_configuration_does_not_exist(self.id)
