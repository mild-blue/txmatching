from tests.solvers.best_solution_use_split_resolution_true import (
    BEST_SOLUTION_use_high_res_resolution_TRUE,
    get_donor_recipient_pairs_from_solution)
from tests.test_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):

    def test_solve_from_example_dataset(self):
        # The two solvers are not exactly comparable. There are some solutions that are missing in all solutions solver:
        # we drop some of the solutions from it, that are subsets of other solutions. But this appears only in some
        # solutions that are kind of subset of the others, so it does not influence the top solutions.
        # TODO https://github.com/mild-blue/txmatching/issues/499
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        ILP_SCORES_NUMBER = 20
        configuration = Configuration(use_high_res_resolution=True,
                                      max_number_of_matchings=ILP_SCORES_NUMBER,
                                      solver_constructor_name='ILPSolver')
        solutions_ilp = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)

        self.assertEqual(ILP_SCORES_NUMBER, len(solutions_ilp))
        self.assertSetEqual(BEST_SOLUTION_use_high_res_resolution_TRUE,
                            get_donor_recipient_pairs_from_solution(solutions_ilp[0].matching_pairs))
        configuration = Configuration(use_high_res_resolution=True,
                                      max_number_of_matchings=1000,
                                      max_debt_for_country=10)

        solutions_all_sol_solver = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertEqual(947, len(solutions_all_sol_solver))
        self.assertSetEqual(BEST_SOLUTION_use_high_res_resolution_TRUE,
                            get_donor_recipient_pairs_from_solution(solutions_all_sol_solver[0].matching_pairs))
        ilp_scores = [sol.score for sol in solutions_ilp]
        all_sol_solver_scores = [sol.score for sol in solutions_all_sol_solver[:ILP_SCORES_NUMBER]]
        self.maxDiff = None
        self.assertListEqual(ilp_scores, all_sol_solver_scores)
