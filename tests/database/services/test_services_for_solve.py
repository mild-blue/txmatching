from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services.config_service import \
    find_config_id_for_configuration
from txmatching.database.services.pairing_result_service import \
    get_pairing_result_comparable_to_config
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete


class TestServiceForSolve(DbTests):
    def test_caching_in_solve_from_configuration(self):
        self.fill_db_with_patients_and_results()

        config_id = find_config_id_for_configuration(Configuration(), 1)
        self.assertIsNotNone(config_id,
                             'there should be 1 config in the database')

        self.assertIsNotNone(get_pairing_result_comparable_to_config(config_id, Configuration(), get_txm_event_complete(1)),
                             'there should be 1 pairing result in the database')
