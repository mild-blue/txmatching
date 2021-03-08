from tests.test_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import (Configuration,
                                                    ManualDonorRecipientScore)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):

    def test_no_new_config_is_saved_if_one_already_exists(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event_complete(txm_event_db_id)
        configuration = Configuration(solver_constructor_name='ILPSolver')
        self.assertEqual(configuration.max_number_of_matchings,
                         len(list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)))

    def test_solve_from_configuration(self):
        txm_event_db_id = self.fill_db_with_patients()
        txm_event = get_txm_event_complete(txm_event_db_id)
        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=4, score=1.0)])
        self.assertEqual(configuration.max_number_of_matchings,
                         len(list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)))

    def test_solve_from_configuration_multiple_countries_old_version(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data2.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        max_country_count = 1
        configuration = Configuration(max_number_of_distinct_countries_in_round=max_country_count,
                                      solver_constructor_name='ILPSolver')
        solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))
        for round in solutions[0].get_rounds():
            self.assertGreaterEqual(1, round.country_count())

    def test_solve_from_configuration_multiple_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for max_country_count in range(1, 3):
            configuration = Configuration(
                solver_constructor_name='ILPSolver',
                max_number_of_distinct_countries_in_round=max_country_count,
                max_number_of_matchings=1)
            solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions))
            for round in solutions[0].get_rounds():
                self.assertEqual(max_country_count, round.country_count())

    def test_solve_from_configuration_forbidden_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data3.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            max_number_of_distinct_countries_in_round=3)
        solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertEqual(configuration.max_number_of_matchings, len(solutions))

    def test_with_sequence_length_limit(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for max_sequence_length in range(1, 5):
            configuration = Configuration(
                solver_constructor_name='ILPSolver',
                use_high_res_resolution=True,
                max_sequence_length=max_sequence_length,
                max_cycle_length=0,
                max_number_of_matchings=3)
            solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions),
                                 f'Failed for {max_sequence_length}')

            real_max_sequence_length = max(
                [max([sequence.length() for sequence in solution.get_sequences()], default=0) for solution
                 in
                 solutions])
            self.assertEqual(max_sequence_length, real_max_sequence_length)

    def test_with_cycle_length_limit(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for max_cycle_length in range(2, 5):
            configuration = Configuration(solver_constructor_name='ILPSolver',
                                          use_high_res_resolution=True,
                                          max_cycle_length=max_cycle_length,
                                          max_sequence_length=0,
                                          max_number_of_matchings=3)
            solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
            self.assertLessEqual(3, len(solutions),
                                 f'Failed for {max_cycle_length}')
            real_max_cycle_length = max(
                [max([cycle.length() for cycle in solution.get_cycles()], default=0) for solution in
                 solutions])
            self.assertEqual(max_cycle_length, real_max_cycle_length, f'Failed for {max_cycle_length}')

    def test_max_debt_between_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for debt in range(1, 4):
            configuration = Configuration(
                solver_constructor_name='ILPSolver',
                use_high_res_resolution=True,
                max_debt_for_country=debt,
                max_number_of_matchings=3)
            solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions),
                                 f'Failed for {debt}')

            max_debt = max(matching.max_debt_from_matching for matching in solutions)
            self.assertEqual(debt, max_debt, f'Fail: max_debt: {max_debt} but configuration said {debt}')

    def test_required_patients(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path('/tests/resources/data_for_required_patients_test.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        required_patient = 5
        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            use_high_res_resolution=True,
            max_number_of_matchings=10,
            max_cycle_length=10)
        solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertLessEqual(1, len(solutions))
        self.assertNotIn(required_patient, {pair.recipient.db_id for pair in solutions[0].matching_pairs})

        configuration = Configuration(
            solver_constructor_name='ILPSolver',
            use_high_res_resolution=True,
            required_patient_db_ids=[required_patient],
            max_number_of_matchings=3,
            max_cycle_length=10)
        solutions = list(solve_from_configuration(configuration, txm_event).calculated_matchings_list)
        self.assertLessEqual(1, len(solutions))
        self.assertIn(required_patient, {pair.recipient.db_id for pair in solutions[0].matching_pairs})

    def test_solver_no_patients(self):
        txm_event = create_or_overwrite_txm_event(name='test')
        solve_from_configuration(Configuration(solver_constructor_name='ILPSolver'), txm_event)
