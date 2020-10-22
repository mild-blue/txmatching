import numpy.testing as testing

from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services.scorer_service import \
    calculate_current_score_matrix


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_caching_in_solve_from_configuration(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        score_matrix = calculate_current_score_matrix(Configuration(max_cycle_length=90), txm_event_db_id)
        testing.assert_array_equal(
            [[-2.0, 18.0],
             [18.0, -2.0]],
            score_matrix)
