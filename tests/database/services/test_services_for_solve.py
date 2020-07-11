import unittest

from kidney_exchange.database.services.config_service import get_config_models
from kidney_exchange.database.services.services_for_solve import get_patients_for_pairing_result, \
    db_matching_to_matching
from kidney_exchange.database.sql_alchemy_schema import PairingResultModel
from kidney_exchange.web import create_app


class TestSolveFromDbAndItsSupportFunctionality(unittest.TestCase):
    def test_caching_in_solve_from_db(self):
        app = create_app()
        with app.app_context():
            self.assertLessEqual(3, len(list(get_config_models())), "there should be at least 3 configs in the database")

            self.assertEqual(2, len(get_patients_for_pairing_result(1)), "Incorrect patients returned for"
                                                                         " pairing result id")

            self.assertEqual(1, len(db_matching_to_matching(PairingResultModel.query.all()[0].calculated_matchings)),
                             "Matching converter has not converted correctly matching from DB. Investigate!")
