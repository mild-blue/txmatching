from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters


@dataclass
class ConfigurationDetailed:
    id: int
    txm_event_id: int
    parameters: ConfigParameters
