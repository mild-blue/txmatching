import unittest

from kidney_exchange.config.configuration import Configuration, RecipientDonorScore
from kidney_exchange.database.services.config_service import save_configuration_as_current
from kidney_exchange.solvers.solve_from_config import solve_from_db
from kidney_exchange.web import create_app


class TestSolveFromDbAndItsSupportFunctionality(unittest.TestCase):
    def test_caching_in_solve_from_db(self):
        app = create_app()
        with app.app_context():
            self.assertEqual(1, len(list(solve_from_db())))

    def test_solve_from_db(self):
        app = create_app()
        with app.app_context():
            configuration = Configuration(
                manual_recipient_donor_scores=[
                    RecipientDonorScore(donor_id=1, recipient_id=4, compatibility_index=1.0)],
                require_new_donor_having_better_match_in_compatibility_index=False)
            save_configuration_as_current(configuration)
            self.assertEqual(1, len(list(solve_from_db())))
