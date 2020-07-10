import unittest

from kidney_exchange.database.services.matching import get_config_models, get_configs_compatible_with_params, \
    get_patients_for_pairing_result, db_matching_to_matching
from kidney_exchange.database.sql_alchemy_schema import PairingResultModel
from kidney_exchange.solvers.solve_from_config import solve_from_db
from kidney_exchange.web import create_app


class TestCompatibilityIndex(unittest.TestCase):
    def test_caching(self):
        app = create_app()
        with app.app_context():
            self.assertEqual(3, len(get_config_models()), "there should be 2 configs in the database")
            self.assertEqual(2,
                             len(get_configs_compatible_with_params(dict({"enforce_same_blood_group": True}))),
                             "the blood group should make one of the configs incompatible")
            self.assertEqual(2,
                             len(get_configs_compatible_with_params(dict({"use_binary_scoring": False}))),
                             "use_binary_scoring should not affect config compatibility")

            self.assertEqual(2, len(get_patients_for_pairing_result(1)))

            self.assertEqual(1, len(db_matching_to_matching(PairingResultModel.query.all()[0].calculated_matchings)))

            self.assertEqual(1, len(solve_from_db()))
