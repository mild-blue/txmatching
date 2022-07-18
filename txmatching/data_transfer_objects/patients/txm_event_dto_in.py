from dataclasses import dataclass
from typing import List, Optional

from txmatching.utils.country_enum import Country
from txmatching.utils.enums import TxmEventState


@dataclass
class TxmEventDTOIn:
    name: str


@dataclass
class TxmDefaultEventDTOIn:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name

    def __post_init__(self):
        if self.id < 0:
            is_id_valid(self.id)


@dataclass
class TxmEventUpdateDTOIn:
    state: Optional[TxmEventState]


@dataclass
class TxmEventExportDTOIn:
    country: Country
    new_txm_event_name: str


@dataclass
class TxmEventCopyPatientsDTOIn:
    txm_event_id_from: int
    txm_event_id_to: int
    donor_ids: List[int]

    def __post_init__(self):
        if self.txm_event_id_from < 0:
            raise ValueError("Invalid txm_event_id_from, it must be greater than 0")

        if self.txm_event_id_to < 0:
            raise ValueError("Invalid txm_event_id_to, it must be greater than 0")

        if self.donor_ids:
            for donor_id in self.donor_ids:
                if donor_id < 0:
                    raise ValueError("Invalid donor_id, it must be greater than 0")


def is_id_valid(id: int):
    if id < 0:
        raise ValueError("Invalid id, it must be greater than 0")


def is_txm_event_id_from_valid(txm_event_id_from: int):
    if txm_event_id_from < 0:
        raise ValueError("Invalid txm_event_id_from, it must be greater than 0")


def is_txm_event_id_to_valid(txm_event_id_to: int):
    if txm_event_id_to < 0:
        raise ValueError("Invalid txm_event_id_to, it must be greater than 0")
