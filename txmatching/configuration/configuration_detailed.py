from dataclasses import dataclass

from txmatching.configuration.configuration import Configuration


@dataclass
class ConfigurationDetailed:
    id: int
    txm_event_id: int
    parameters: Configuration
