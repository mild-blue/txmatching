import unittest

from tests.solvers.best_solution_use_split_resolution_true import (
    BEST_SOLUTION_USE_SPLIT_RESOLUTION_TRUE,
    get_donor_recipient_pairs_from_solution)
from tests.test_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import (Configuration,
                                                    ManualDonorRecipientScore)
from txmatching.database.services.txm_event_service import get_txm_event
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):

    def test_no_new_config_is_saved_if_one_already_exists(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event(txm_event_db_id)
        self.assertEqual(1, len(list(solve_from_configuration(
            Configuration(solver_constructor_name='ILPSolver'), txm_event).calculated_matchings_list)))

    def test_solve_from_configuration(self):
        txm_event_db_id = self.fill_db_with_patients()
        txm_event = get_txm_event(txm_event_db_id)
        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=4, score=1.0)])
        self.assertEqual(1, len(list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)))

    @unittest.skip('Support for limitation of number of countries in round has not yet been implemented')
    # TODO: improve the code https://github.com/mild-blue/txmatching/issues/430
    def test_solve_from_configuration_multiple_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data2.xlsx'))
        txm_event = get_txm_event(txm_event_db_id)
        max_country_count = 1
        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            max_number_of_distinct_countries_in_round=max_country_count)
        solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))
        for round in solutions[0].get_rounds():
            self.assertGreaterEqual(1, round.country_count())

    def test_solve_from_configuration_forbidden_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data3.xlsx'))
        txm_event = get_txm_event(txm_event_db_id)
        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            max_number_of_distinct_countries_in_round=3)
        solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))

    def test_solve_from_example_dataset(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event(txm_event_db_id)
        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            use_split_resolution=True,
            max_matchings_to_store_in_db=1000)
        solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))
        self.assertSetEqual(BEST_SOLUTION_USE_SPLIT_RESOLUTION_TRUE,
                            get_donor_recipient_pairs_from_solution(solutions[0].matching_pairs))

    def test_with_sequence_length_limit(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event(txm_event_db_id)
        for max_sequence_length in range(1, 6):
            configuration = Configuration(
                solver_constructor_name='ILPSolver',
                use_split_resolution=True, max_sequence_length=max_sequence_length, max_cycle_length=0)
            solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
            self.assertEqual(1, len(solutions))

            real_max_sequence_length = max(
                [max([sequence.length() for sequence in solution.get_sequences()]) for solution
                 in
                 solutions])
            self.assertGreaterEqual(max_sequence_length, real_max_sequence_length)

    def test_with_cycle_length_limit(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event(txm_event_db_id)
        for max_cycle_length in range(2, 5):
            configuration = Configuration(solver_constructor_name='ILPSolver', use_split_resolution=True,
                                          max_cycle_length=max_cycle_length, max_sequence_length=0)
            solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
            self.assertEqual(1, len(solutions))
            real_max_cycle_length = max(
                [max([cycle.length() for cycle in solution.get_cycles()], default=0) for solution in
                 solutions])
            self.assertGreaterEqual(max_cycle_length, real_max_cycle_length)

    def test_solver_no_patients(self):
        txm_event = create_or_overwrite_txm_event(name='test')
        solve_from_configuration(Configuration(solver_constructor_name='ILPSolver'), txm_event)
