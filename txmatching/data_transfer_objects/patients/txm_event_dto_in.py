from dataclasses import dataclass
from typing import List, Optional

from txmatching.database.services.txm_event_service import does_txm_event_exist
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
        is_greater_than_zero("id", self.id)


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
        validate_txm_event_from(self.txm_event_id_from)
        validate_txm_event_to(self.txm_event_id_to)

        for donor_id in self.donor_ids:
            is_greater_than_zero("donor_id", donor_id)


def validate_txm_event_from(txm_event_id_from: int):
    if not does_txm_event_exist(txm_event_id_from):
        raise ValueError(f"Invalid txm_event_id_from with value {txm_event_id_from}. Txm Event with given id does not exist.")


def validate_txm_event_to(txm_event_id_to: int):
    if not does_txm_event_exist(txm_event_id_to):
        raise ValueError(f"Invalid txm_event_id_to with value {txm_event_id_to}. Txm Event with given id does not exist.")


def is_greater_than_zero(name: str, value: int):
    if value < 0:
        raise ValueError(f"Invalid {name} with value {value}, it must be greater than 0")
