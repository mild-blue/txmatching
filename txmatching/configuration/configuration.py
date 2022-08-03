from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.txm_event_service import raise_error_if_txm_event_does_not_exist
# from txmatching.database.services.config_service import raise_error_if_configuration_does_not_exist
from txmatching.database.sql_alchemy_schema import ConfigModel


@dataclass
class Configuration:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name
    txm_event_id: int
    parameters: ConfigParameters

    def __post_init__(self):
        raise_error_if_configuration_does_not_exist(self.id)

        raise_error_if_txm_event_does_not_exist(self.txm_event_id)

# it's not possible to place this function in config_service.py because of circular import
def raise_error_if_configuration_does_not_exist(configuration_id):
    if ConfigModel.query.filter_by(id=configuration_id).first() is None:
        raise ValueError(f"Configuration with id {configuration_id} does not exist")
