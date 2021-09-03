from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters


@dataclass
class Configuration:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name
    txm_event_id: int
    parameters: ConfigParameters
