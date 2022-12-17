from dataclasses import dataclass
from typing import List, Optional

from txmatching.database.services.patient_service import \
    raise_error_if_donor_in_txm_event_doesnt_exist
from txmatching.database.services.txm_event_service import \
    raise_error_if_txm_event_does_not_exist
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import StrictnessType, TxmEventState


@dataclass
class TxmEventDTOIn:
    name: str
    strictness_type: StrictnessType = StrictnessType.STRICT


@dataclass
class TxmDefaultEventDTOIn:
    # pylint:disable=invalid-name
    id: int

    # pylint:enable=invalid-name

    def __post_init__(self):
        raise_error_if_txm_event_does_not_exist(self.id)


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
        raise_error_if_txm_event_does_not_exist(self.txm_event_id_from)

        raise_error_if_txm_event_does_not_exist(self.txm_event_id_to)

        for donor_id in self.donor_ids:
            raise_error_if_donor_in_txm_event_doesnt_exist(self.txm_event_id_from, donor_id)
