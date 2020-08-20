from kidney_exchange.database.services.config_service import get_config_models
from kidney_exchange.database.services.services_for_solve import get_patients_for_pairing_result
from tests.test_utilities.prepare_app import DbTests


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_caching_in_solve_from_db(self):
        self.assertEqual(1, len(list(get_config_models())),
                         "there should be 1 config in the database")

        self.assertEqual(4, len(get_patients_for_pairing_result(1)), "Incorrect patients returned for"
                                                                     " pairing result id")
