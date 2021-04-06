from typing import List

from txmatching.auth.exceptions import GuardException
from txmatching.database.services.txm_event_service import get_txm_event_base
from txmatching.utils.enums import TxmEventState


def guard_open_txm_event(txm_event_id: int):
    """
    Checks that the txm event is opened
    """
    guard_txm_event_state(txm_event_id, [TxmEventState.OPEN])


def guard_txm_event_state(txm_event_id: int, txm_event_states: List[TxmEventState]):
    """
    Checks that the txm event has the required state
    """
    txm_event = get_txm_event_base(txm_event_id)
    if txm_event.state not in txm_event_states:
        raise GuardException(
            f'TXM event {txm_event_id} has state {txm_event.state} but required states are {txm_event_states}.'
        )
