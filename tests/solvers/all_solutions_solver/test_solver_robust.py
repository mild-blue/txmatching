from tests.solvers.prepare_txm_event_with_many_solutions import prepare_txm_event_with_too_many_solutions
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import Solver


class TestLargeMatchingDoesNotFail(DbTests):
    def testing_computation_for_patients_that_create_extremely_many_matchings(self):
        txm_event = prepare_txm_event_with_too_many_solutions()
        self.assertEqual(1, len(list(solve_from_configuration(
            ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver, max_number_of_matchings=1), txm_event
        ).calculated_matchings_list)))
