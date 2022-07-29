from dataclasses import dataclass
from typing import List, Optional

from txmatching.database.services.patient_service import does_donor_in_txm_event_exist
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
        if self.id < 0:
            raise ValueError(f"Invalid id with value {self.id}, it must be greater than 0")


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
        validate_txm_event("from", self.txm_event_id_from)
        validate_txm_event("to", self.txm_event_id_to)

        for donor_id in self.donor_ids:
            if not does_donor_in_txm_event_exist(self.txm_event_id_from, donor_id):
                raise ValueError(f"Donor with id {donor_id} does not exist in txm event with id {self.txm_event_id_from}")


def validate_txm_event(dest: str, txm_event_id: int):
    if not does_txm_event_exist(txm_event_id):
        raise ValueError(f"Invalid txm_event_id_{dest} with value {txm_event_id}. Txm Event with given id does not exist.")
