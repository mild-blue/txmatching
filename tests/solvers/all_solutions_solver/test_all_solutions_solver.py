from local_testing_utilities.generate_patients import (
    GENERATED_TXM_EVENT_NAME, SMALL_DATA_FOLDER,
    SMALL_DATA_FOLDER_WITH_NO_SOLUTION, SMALL_DATA_FOLDER_WITH_ROUND,
    store_generated_patients_from_folder)
from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.solvers.ilp_solver.test_ilp_solver import _set_donor_blood_group
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.configuration.config_parameters import (
    ConfigParameters, ManualDonorRecipientScore)
from txmatching.database.db import db
from txmatching.database.services.txm_event_service import (
    get_txm_event_complete, get_txm_event_db_id_by_name)
from txmatching.database.sql_alchemy_schema import DonorModel
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import HLACrossmatchLevel, Solver
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.database.sql_alchemy_schema import DonorModel
from txmatching.database.db import db

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
        for max_sequence_length in range(1, 6):
            config_parameters = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                                 use_high_resolution=True, max_sequence_length=max_sequence_length,
                                                 max_number_of_matchings=1000)
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
                                                 max_number_of_matchings=1000)
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
            max_number_of_matchings=10,
            max_cycle_length=10)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertLessEqual(1, len(solutions))
        self.assertNotIn(required_patient, {pair.recipient.db_id for pair in solutions[0].matching_pairs})

        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            use_high_resolution=True,
            required_patient_db_ids=[required_patient],
            max_number_of_matchings=3,
            max_cycle_length=10)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertLessEqual(1, len(solutions))
        self.assertIn(required_patient, {pair.recipient.db_id for pair in solutions[0].matching_pairs})

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
        self.assertEqual(len(solution), 1)

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
        self.assertEqual(len(solutions), 1)

    def test_handling_correctly_multiple_donors(self):
        # 1. create txm event
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))

        self.login_with_role(UserRole.ADMIN)

        # 2. alter donor table so that there's 2 donors relating to the same recipient
        donor_id_to_change = 15
        recipient_id_for_error = 13
        DonorModel.query.filter(DonorModel.id == donor_id_to_change).update(
            {'recipient_id': recipient_id_for_error})
        db.session.commit()

        # 3. calcualate
        solutions = solve_from_configuration(
            ConfigParameters(), get_txm_event_complete(txm_event_db_id)).calculated_matchings_list

        # 4. check if the recipient is not matched with more than one donor
        for solution in solutions:
            recipient_ids = [pair.recipient.db_id for pair in solution.matching_pairs]

            seen = set()
            duplicates = [x for x in recipient_ids if x in seen or seen.add(x)]

            if duplicates:
                raise Exception(f'Recipient/recipients with id/ids {duplicates} is/are in matching more than once')
