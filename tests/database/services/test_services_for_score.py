import unittest

import numpy as np
import numpy.testing as testing

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.database.services.config_service import save_configuration_as_current
from kidney_exchange.database.services.scorer_service import calculate_current_score_matrix
from kidney_exchange.scorers.hla_additive_scorer import BLOOD_GROUP_COMPATIBILITY_BONUS
from kidney_exchange.web import create_app


class TestSolveFromDbAndItsSupportFunctionality(unittest.TestCase):
    def test_caching_in_solve_from_db(self):
        app = create_app()
        with app.app_context():
            save_configuration_as_current(
                Configuration(require_new_donor_having_better_match_in_compatibility_index=False)
            )
            score_matrix = calculate_current_score_matrix()
            testing.assert_array_equal(
                np.array([[np.nan, BLOOD_GROUP_COMPATIBILITY_BONUS], [BLOOD_GROUP_COMPATIBILITY_BONUS, np.nan]]),
                score_matrix)
