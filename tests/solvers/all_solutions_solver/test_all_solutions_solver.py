from local_testing_utilities.generate_patients import (
    GENERATED_TXM_EVENT_NAME, THEORETICAL_DOUBLE_TXM_EVENT_NAME, SMALL_DATA_FOLDER_THEORETICAL,
    SMALL_DATA_FOLDER_WITH_ROUND, store_generated_patients_from_folder)
from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.solvers.ilp_solver.test_ilp_solver import _set_donor_blood_group
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import (
    ConfigParameters, ManualDonorRecipientScore)
from txmatching.database.services.txm_event_service import (
    get_txm_event_complete, get_txm_event_db_id_by_name)
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import HLACrossmatchLevel, Solver
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_no_new_config_is_saved_if_one_already_exists(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event_complete(txm_event_db_id)
        self.assertEqual(1, len(list(solve_from_configuration(
            ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver), txm_event
        ).calculated_matchings_list)))

    def test_solve_from_configuration(self):
        txm_event_db_id = self.fill_db_with_patients()
        txm_event = get_txm_event_complete(txm_event_db_id)
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=4, score=1.0)])
        self.assertEqual(1, len(list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)))

    def test_solve_from_configuration_multiple_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data2.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        max_country_count = 1
        config_parameters = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                             max_number_of_distinct_countries_in_round=max_country_count)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))
        for round in solutions[0].get_rounds():
            self.assertGreaterEqual(1, round.country_count())

    def test_solve_from_configuration_forbidden_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data3.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        config_parameters = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                             max_number_of_distinct_countries_in_round=3)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))

    def test_with_sequence_length_limit(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for max_sequence_length in range(1, 5):
            config_parameters = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                                 use_high_resolution=True, max_sequence_length=max_sequence_length,
                                                 max_cycle_length=0,
                                                 max_number_of_matchings=5)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertEqual(max_sequence_length,
                             max([max([sequence.length() for sequence in solution.get_sequences()]) for solution in
                                  solutions]))

    def test_with_cycle_length_limit(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for max_cycle_length in range(2, 5):
            config_parameters = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                                 use_high_resolution=True, max_cycle_length=max_cycle_length,
                                                 max_sequence_length=0,
                                                 max_number_of_matchings=5)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertEqual(max_cycle_length,
                             max([max([cycle.length() for cycle in solution.get_cycles()], default=0) for solution in
                                  solutions]))

    def test_max_blood_group_zero_debt_between_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        txm_event.active_and_valid_donors_dict = {i: _set_donor_blood_group(donor) for i, donor in
                                                  txm_event.active_and_valid_donors_dict.items()}
        for debt in range(0, 4):
            config_parameters = ConfigParameters(
                solver_constructor_name=Solver.AllSolutionsSolver,
                use_high_resolution=True,
                max_debt_for_country_for_blood_group_zero=debt,
                max_number_of_matchings=7,
                hla_crossmatch_level=HLACrossmatchLevel.NONE)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions),
                                 f'Failed for {debt}')

            max_debt = max(matching.max_blood_group_zero_debt_from_matching for matching in solutions)
            self.assertEqual(debt, max_debt, f'Fail: max_debt: {max_debt} but configuration said {debt}')

    def test_max_debt_between_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for debt in range(1, 4):
            config_parameters = ConfigParameters(
                solver_constructor_name=Solver.AllSolutionsSolver,
                use_high_resolution=True,
                max_debt_for_country=debt,
                max_number_of_matchings=3,
                hla_crossmatch_level=HLACrossmatchLevel.NONE)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions),
                                 f'Failed for {debt}')

            max_debt = max(matching.max_debt_from_matching for matching in solutions)
            self.assertEqual(debt, max_debt, f'Fail: max_debt: {max_debt} but configuration said {debt}')

    def test_required_patients(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path('/tests/resources/data_for_required_patients_test.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        required_patient = 5
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            use_high_resolution=True,
            max_number_of_matchings=1)
        solutions_not_required = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions_not_required))
        self.assertNotIn(required_patient, {pair.recipient.db_id for pair in solutions_not_required[0].matching_pairs})

        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            use_high_resolution=True,
            required_patient_db_ids=[required_patient],
            max_number_of_matchings=1)
        solutions_required = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions_required))
        self.assertIn(required_patient, {pair.recipient.db_id for pair in solutions_required[0].matching_pairs})

    def test_solver_no_patients(self):
        txm_event = create_or_overwrite_txm_event(name='test')
        solve_from_configuration(ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
        ), txm_event)

    def test_manual_scores_set_manual_score_of_original_pair(self):
        store_generated_patients_from_folder(SMALL_DATA_FOLDER_WITH_ROUND)

        txm_event = get_txm_event_complete(get_txm_event_db_id_by_name(GENERATED_TXM_EVENT_NAME))
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=1, score=7.0)])
        solution = solve_from_configuration(config_parameters, txm_event).calculated_matchings_list
        self.assertEqual(1, len(solution))

    def test_theoretical_and_double_chain_antibodies(self):
        # the data is prepared such that both recipients have double antibodies. One has
        # antibodies compatible with the bridinging donor, one has with normal donor. We are testing that
        # theoretical antibodies are correctly parsed and then correctly ignored in crossmatch. Moreover, we
        # test that double antibodies are correctly applied.
        store_generated_patients_from_folder(SMALL_DATA_FOLDER_THEORETICAL,
                                             THEORETICAL_DOUBLE_TXM_EVENT_NAME)
        txm_event = get_txm_event_complete(get_txm_event_db_id_by_name(THEORETICAL_DOUBLE_TXM_EVENT_NAME))

        config_parameters = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver)
        solution = solve_from_configuration(config_parameters, txm_event).calculated_matchings_list
        self.assertListEqual([('CZE_T2', 'CZE_T0R'), ('CZE_T0', 'CZE_T1R')],
                             [(p.donor.medical_id, p.recipient.medical_id) for p in solution[0].matching_pairs])
        self.assertListEqual([('CZE_T2', 'CZE_T0R')],
                             [(p.donor.medical_id, p.recipient.medical_id) for p in solution[1].matching_pairs])

    def test_manual_scores_set_manual_score_of_every_pair_to_negative(self):
        store_generated_patients_from_folder(SMALL_DATA_FOLDER_WITH_ROUND)

        txm_event = get_txm_event_complete(get_txm_event_db_id_by_name(GENERATED_TXM_EVENT_NAME))
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=3, recipient_db_id=2, score=-1.0),
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=2, score=-1.0),
                ManualDonorRecipientScore(donor_db_id=2, recipient_db_id=2, score=-1.0),
                ManualDonorRecipientScore(donor_db_id=3, recipient_db_id=1, score=-1.0),
                ManualDonorRecipientScore(donor_db_id=2, recipient_db_id=1, score=-1.0),
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=1, score=-1.0)])
        solutions = solve_from_configuration(config_parameters, txm_event).calculated_matchings_list
        self.assertEqual(len(solutions), 0)

    def test_manual_scores_make_cycle(self):
        store_generated_patients_from_folder(SMALL_DATA_FOLDER_WITH_ROUND)

        txm_event = get_txm_event_complete(get_txm_event_db_id_by_name(GENERATED_TXM_EVENT_NAME))
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=2, recipient_db_id=1, score=4.0),
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=2, score=1.0),
                ManualDonorRecipientScore(donor_db_id=3, recipient_db_id=1, score=1.0),
            ])
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))
