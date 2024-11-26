from dataclasses import dataclass

from txmatching.database.sql_alchemy_schema import ConfigModel


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
        #it is not possible to create a function that checks it in config_service.py because of the circular dependency
        if ConfigModel.query.get(self.id) is None:
            raise ValueError(f'Configuration with id {self.id} does not exist')
