import numpy.testing as testing

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.database.services.config_service import save_configuration_as_current
from kidney_exchange.database.services.scorer_service import calculate_current_score_matrix
from tests.test_utilities.prepare_app import DbTests


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_caching_in_solve_from_db(self):
        save_configuration_as_current(
            Configuration(require_new_donor_having_better_match_in_compatibility_index=False)
        )
        score_matrix = calculate_current_score_matrix()
        testing.assert_array_equal(
            [['Original Donor recipient tuple', '18.0'],
             ['18.0', 'Original Donor recipient tuple']],
            score_matrix)
