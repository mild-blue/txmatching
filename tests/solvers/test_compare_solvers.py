from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from tests.solvers.best_solution_use_split_resolution_true import (
    BEST_SOLUTION_use_high_resolution_TRUE,
    get_donor_recipient_pairs_from_solution)
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import HLACrossmatchLevel, Solver
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):

    def test_solve_from_example_dataset(self):
        # The two solvers are not exactly comparable. There are some solutions that are missing in all solutions solver:
        # we drop some of the solutions from it, that are subsets of other solutions. But this appears only in some
        # solutions that are kind of subset of the others, so it does not influence the top solutions.
        # TODO https://github.com/mild-blue/txmatching/issues/499
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        NUMBER_OF_SOLUTIONS = 10
        config_parameters = ConfigParameters(use_high_resolution=True,
                                             max_number_of_matchings=NUMBER_OF_SOLUTIONS,
                                             solver_constructor_name=Solver.ILPSolver,
                                             hla_crossmatch_level=HLACrossmatchLevel.NONE,
                                             max_matchings_in_ilp_solver=NUMBER_OF_SOLUTIONS)
        solutions_ilp = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)

        self.assertEqual(NUMBER_OF_SOLUTIONS, len(solutions_ilp))
        self.assertSetEqual(BEST_SOLUTION_use_high_resolution_TRUE,
                            get_donor_recipient_pairs_from_solution(solutions_ilp[0].matching_pairs))
        config_parameters = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                             use_high_resolution=True,
                                             max_number_of_matchings=NUMBER_OF_SOLUTIONS,
                                             max_debt_for_country=10,
                                             hla_crossmatch_level=HLACrossmatchLevel.NONE)

        solutions_all_sol_solver = list(
            solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertEqual(NUMBER_OF_SOLUTIONS, len(solutions_all_sol_solver))
        self.assertSetEqual(BEST_SOLUTION_use_high_resolution_TRUE,
                            get_donor_recipient_pairs_from_solution(solutions_all_sol_solver[0].matching_pairs))
        ilp_scores = [sol.score for sol in solutions_ilp]
        all_sol_solver_scores = [sol.score for sol in solutions_all_sol_solver]
        self.maxDiff = None

        for i in range(NUMBER_OF_SOLUTIONS):
            print("ilp solver selected paths     ", [(pair.donor.db_id, pair.recipient.db_id) for pair in solutions_ilp[i].matching_pairs], solutions_ilp[i].score)
            print("all sol solver selected paths ", [(pair.donor.db_id, pair.recipient.db_id) for pair in solutions_all_sol_solver[i].matching_pairs], solutions_all_sol_solver[i].score)
            print()
        self.assertListEqual(ilp_scores, all_sol_solver_scores)
