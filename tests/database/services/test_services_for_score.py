import unittest

import numpy.testing as testing

from txmatching.config.configuration import Configuration
from txmatching.database.services.config_service import save_configuration_as_current
from txmatching.database.services.scorer_service import calculate_current_score_matrix
from txmatching.web import create_app


class TestSolveFromDbAndItsSupportFunctionality(unittest.TestCase):
    def test_caching_in_solve_from_db(self):
        app = create_app()
        with app.app_context():
            save_configuration_as_current(
                Configuration(require_new_donor_having_better_match_in_compatibility_index=False)
            )
            score_matrix = calculate_current_score_matrix()
            testing.assert_array_equal(
                [['Original Donor recipient tuple', '18.0'],
                 ['18.0', 'Original Donor recipient tuple']],
                score_matrix)
