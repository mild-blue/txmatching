from dataclasses import dataclass
from typing import List, Optional

from txmatching.database.services.patient_service import \
    does_donor_in_txm_event_exist
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
        does_txm_event_exist(self.id)


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
        does_txm_event_exist(self.txm_event_id_from)

        does_txm_event_exist(self.txm_event_id_to)

        for donor_id in self.donor_ids:
            does_donor_in_txm_event_exist(self.txm_event_id_from, donor_id)
