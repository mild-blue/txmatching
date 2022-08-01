from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.txm_event_service import does_txm_event_exist
from txmatching.database.sql_alchemy_schema import ConfigModel


@dataclass
class Configuration:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name
    txm_event_id: int
    parameters: ConfigParameters

    def __post_init__(self):
        if not does_configuration_exist(self.id):
            raise ValueError(f"Configuration with id {self.id} does not exist")

        does_txm_event_exist(self.txm_event_id)


def does_configuration_exist(configuration_id):
    return ConfigModel.query.filter_by(id=configuration_id).first() is not None
