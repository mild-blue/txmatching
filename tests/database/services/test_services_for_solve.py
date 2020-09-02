from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.config_service import get_config_models
from txmatching.database.services.services_for_solve import \
    get_patients_for_pairing_result


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_caching_in_solve_from_db(self):
        self.fill_db_with_patients_and_results()
        self.assertEqual(1, len(list(get_config_models())),
                         'there should be 1 config in the database')

        self.assertEqual(4, len(get_patients_for_pairing_result(1)), 'Incorrect patients returned for'
                                                                     ' pairing result id')
