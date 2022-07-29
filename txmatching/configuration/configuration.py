from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.parsing_issue_service import is_parameter_positive


@dataclass
class Configuration:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name
    txm_event_id: int
    parameters: ConfigParameters

    def __post_init__(self):
        is_parameter_positive("configuration id", self.id)
        is_parameter_positive("txm event id", self.txm_event_id)
