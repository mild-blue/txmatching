from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.config_service import \
    get_latest_config_model_for_txm_event


class TestServiceForSolve(DbTests):
    def test_caching_in_solve_from_configuration(self):
        self.fill_db_with_patients_and_results()
        self.assertIsNotNone(get_latest_config_model_for_txm_event(1), 'there should be 1 config in the database')
