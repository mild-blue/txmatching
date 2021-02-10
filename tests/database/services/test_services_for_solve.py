from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.config_service import \
    get_latest_configuration_db_id_for_txm_event
from txmatching.database.services.txm_event_service import get_txm_event_all


class TestServiceForSolve(DbTests):
    def test_caching_in_solve_from_configuration(self):
        self.fill_db_with_patients_and_results()
        self.assertIsNotNone(get_latest_configuration_db_id_for_txm_event(get_txm_event_all(1)),
                             'there should be 1 config in the database')
