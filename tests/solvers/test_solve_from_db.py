from tests.test_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import (Configuration,
                                                    ManualDonorRecipientScore)
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_no_new_config_is_saved_if_one_already_exists(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        self.assertEqual(1, len(list(solve_from_configuration(Configuration(), txm_event_db_id).calculated_matchings_list)))

    def test_solve_from_configuration(self):
        txm_event_db_id = self.fill_db_with_patients()
        configuration = Configuration(
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=4, score=1.0)])
        self.assertEqual(1, len(list(solve_from_configuration(configuration, txm_event_db_id).calculated_matchings_list)))

    def test_solve_from_configuration_multiple_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data2.xlsx'))
        max_country_count = 1
        configuration = Configuration(max_number_of_distinct_countries_in_round=max_country_count)
        solutions = list(solve_from_configuration(configuration, txm_event_db_id).calculated_matchings_list)
        self.assertEqual(1, len(solutions))
        for round in solutions[0].get_rounds():
            self.assertGreaterEqual(1, round.country_count())

    def test_solve_from_configuration_forbidden_countries(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data3.xlsx'))
        configuration = Configuration(max_number_of_distinct_countries_in_round=3)
        solutions = list(solve_from_configuration(configuration, txm_event_db_id).calculated_matchings_list)
        self.assertEqual(1, len(solutions))

    def test_solve_from_example_dataset(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        configuration = Configuration(use_split_resolution=True)
        solutions = list(solve_from_configuration(configuration, txm_event_db_id).calculated_matchings_list)
        self.assertEqual(872, len(solutions))

    def test_solver_no_patients(self):
        create_or_overwrite_txm_event(name='test')
        solve_from_configuration(Configuration(), txm_event_db_id=1)
