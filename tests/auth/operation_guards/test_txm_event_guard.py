from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.exceptions import GuardException
from txmatching.auth.operation_guards.txm_event_guard import \
    guard_open_txm_event
from txmatching.database.services.txm_event_service import set_txm_event_state
from txmatching.utils.enums import TxmEventState


class TestCountryGuards(DbTests):

    def test_guard_open_txm_event(self):
        txm_event = create_or_overwrite_txm_event('txm_event_1')

        set_txm_event_state(txm_event.db_id, TxmEventState.OPEN)
        guard_open_txm_event(txm_event.db_id)

        set_txm_event_state(txm_event.db_id, TxmEventState.CLOSED)
        with self.assertRaises(GuardException):
            guard_open_txm_event(txm_event.db_id)
