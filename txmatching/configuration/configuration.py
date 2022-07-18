from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters


@dataclass
class Configuration:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name
    txm_event_id: int
    parameters: ConfigParameters

    def __post_init__(self):
        if self.id:
            is_conf_id_valid(self.id)

        if self.txm_event_id:
            is_txm_event_id_valid(self.txm_event_id)


def is_conf_id_valid(config_id: int):
    if config_id < 0:
        raise ValueError("Invalid id, it must be greater than 0")


def is_txm_event_id_valid(txm_event_id: int):
    if txm_event_id < 0:
        raise ValueError("Invalid txm_event_id, it must be greater than 0")
