from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.data_transfer_objects import txm_event
from txmatching.database.services.txm_event_service import get_txm_event_complete, raise_error_if_txm_event_does_not_exist
from txmatching.database.sql_alchemy_schema import ConfigModel, RecipientModel


@dataclass
class Configuration:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name
    txm_event_id: int
    parameters: ConfigParameters

    def __post_init__(self):
        raise_error_if_txm_event_does_not_exist(self.txm_event_id)

        # it is not possible to create a function that checks it in config_service.py because of the circular dependency
        config_model = ConfigModel.query.get(self.id)
        if config_model is None or config_model.txm_event_id != self.txm_event_id:
            raise ValueError(f"Configuration with id {self.id} does not exist in txm_event with id {self.txm_event_id}")
