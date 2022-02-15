from local_testing_utilities.generate_patients import store_generated_patients_from_folder, SMALL_DATA_FOLDER, \
    GENERATED_TXM_EVENT_NAME, SMALL_DATA_FOLDER_WITH_ROUND
from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import (
    ConfigParameters, ManualDonorRecipientScore)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete, get_txm_event_db_id_by_name
from txmatching.patients.patient import Donor
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLACrossmatchLevel, Solver
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):

    def test_no_new_config_is_saved_if_one_already_exists(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event_complete(txm_event_db_id)
        config_parameters = ConfigParameters(solver_constructor_name=Solver.ILPSolver)
        self.assertGreaterEqual(config_parameters.max_number_of_matchings,
                         len(list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)))

    def test_solve_from_configuration(self):
        txm_event_db_id = self.fill_db_with_patients()
        txm_event = get_txm_event_complete(txm_event_db_id)
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.ILPSolver,
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=4, score=1.0)])
        self.assertGreaterEqual(config_parameters.max_number_of_matchings,
                         len(list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)))

    def test_solve_from_configuration_multiple_countries_old_version(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data2.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        max_country_count = 1
        config_parameters = ConfigParameters(max_number_of_distinct_countries_in_round=max_country_count,
                                             solver_constructor_name=Solver.ILPSolver)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertEqual(1, len(solutions))
        for round in solutions[0].get_rounds():
            self.assertGreaterEqual(1, round.country_count())

    def test_solve_from_configuration_multiple_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for max_country_count in range(1, 3):
            config_parameters = ConfigParameters(
                solver_constructor_name=Solver.ILPSolver,
                max_number_of_distinct_countries_in_round=max_country_count,
                max_number_of_matchings=1,
                hla_crossmatch_level=HLACrossmatchLevel.NONE)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions))
            for round in solutions[0].get_rounds():
                self.assertEqual(max_country_count, round.country_count())

    def test_solve_from_configuration_forbidden_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data3.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.ILPSolver,
            max_number_of_distinct_countries_in_round=3)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertGreaterEqual(config_parameters.max_number_of_matchings, len(solutions))

    def test_with_sequence_length_limit(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for max_sequence_length in range(1, 5):
            config_parameters = ConfigParameters(
                solver_constructor_name=Solver.ILPSolver,
                use_high_resolution=True,
                max_sequence_length=max_sequence_length,
                max_cycle_length=0,
                max_number_of_matchings=3,
                hla_crossmatch_level=HLACrossmatchLevel.NONE)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
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
            config_parameters = ConfigParameters(solver_constructor_name=Solver.ILPSolver,
                                                 use_high_resolution=True,
                                                 max_cycle_length=max_cycle_length,
                                                 max_sequence_length=0,
                                                 max_number_of_matchings=3)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertLessEqual(3, len(solutions),
                                 f'Failed for {max_cycle_length}')
            real_max_cycle_length = max(
                [max([cycle.length() for cycle in solution.get_cycles()], default=0) for solution in
                 solutions])
            self.assertEqual(max_cycle_length, real_max_cycle_length, f'Failed for {max_cycle_length}')

    def test_max_debt_between_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        for debt in range(0, 4):
            config_parameters = ConfigParameters(
                solver_constructor_name=Solver.ILPSolver,
                use_high_resolution=True,
                max_debt_for_country=debt,
                max_number_of_matchings=3,
                hla_crossmatch_level=HLACrossmatchLevel.NONE)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions),
                                 f'Failed for {debt}')

            max_debt = max(matching.max_debt_from_matching for matching in solutions)
            self.assertEqual(debt, max_debt, f'Fail: max_debt: {max_debt} but configuration said {debt}')

    def test_max_blood_group_zero_debt_between_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        txm_event.active_donors_dict = {i: _set_donor_blood_group(donor) for i, donor in
                                        txm_event.active_donors_dict.items()}
        for debt in range(0, 4):
            config_parameters = ConfigParameters(
                solver_constructor_name=Solver.ILPSolver,
                use_high_resolution=True,
                max_debt_for_country_for_blood_group_zero=debt,
                max_number_of_matchings=7,
                hla_crossmatch_level=HLACrossmatchLevel.NONE)
            solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
            self.assertLessEqual(1, len(solutions),
                                 f'Failed for {debt}')

            max_debt = max(matching.max_blood_group_zero_debt_from_matching for matching in solutions)
            self.assertEqual(debt, max_debt, f'Fail: max_debt: {max_debt} but configuration said {debt}')

        self.assertEqual(-1, solutions[0].get_blood_group_zero_debt_for_country(Country.CZE))
        self.assertEqual(2, solutions[0].get_blood_group_zero_debt_for_country(Country.IND))
        self.assertEqual(-1, solutions[0].get_blood_group_zero_debt_for_country(Country.CAN))

    def test_required_patients(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path('/tests/resources/data_for_required_patients_test.xlsx'))
        txm_event = get_txm_event_complete(txm_event_db_id)
        required_patient = 5
        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.ILPSolver,
            use_high_resolution=True,
            max_number_of_matchings=10,
            max_cycle_length=10)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertLessEqual(1, len(solutions))
        self.assertNotIn(required_patient, {pair.recipient.db_id for pair in solutions[0].matching_pairs})

        config_parameters = ConfigParameters(
            solver_constructor_name=Solver.ILPSolver,
            use_high_resolution=True,
            required_patient_db_ids=[required_patient],
            max_number_of_matchings=3,
            max_cycle_length=10)
        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)
        self.assertLessEqual(1, len(solutions))
        self.assertIn(required_patient, {pair.recipient.db_id for pair in solutions[0].matching_pairs})

    def test_solver_no_patients(self):
        txm_event = create_or_overwrite_txm_event(name='test')
        solve_from_configuration(ConfigParameters(solver_constructor_name=Solver.ILPSolver), txm_event)

    def test_solver_small(self):
        store_generated_patients_from_folder(SMALL_DATA_FOLDER)

        txm_event = get_txm_event_complete(get_txm_event_db_id_by_name(GENERATED_TXM_EVENT_NAME))
        solution = solve_from_configuration(ConfigParameters(solver_constructor_name=Solver.ILPSolver), txm_event)
        self.assertEqual(len(solution.calculated_matchings_list), 1)

    def test_solver_small_with_round(self):
        store_generated_patients_from_folder(SMALL_DATA_FOLDER_WITH_ROUND)

        txm_event = get_txm_event_complete(get_txm_event_db_id_by_name(GENERATED_TXM_EVENT_NAME))
        solution = solve_from_configuration(ConfigParameters(solver_constructor_name=Solver.ILPSolver), txm_event)
        self.assertEqual(len(solution.calculated_matchings_list), 1)


def _set_donor_blood_group(donor: Donor) -> Donor:
    if donor.db_id % 2 == 0:
        donor.parameters.blood_group = BloodGroup.ZERO
    return donor
