from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services.config_service import \
    find_config_db_id_for_configuration_and_data
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete


class TestServiceForSolve(DbTests):
    def test_caching_in_solve_from_configuration(self):
        self.fill_db_with_patients_and_results()
        self.assertIsNotNone(find_config_db_id_for_configuration_and_data(Configuration(), get_txm_event_complete(1)),
                             'there should be 1 config in the database')
