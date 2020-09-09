from tests.test_utilities.prepare_app import DbTests
from txmatching.config.configuration import Configuration, ManualDonorRecipientScore
from txmatching.database.services.config_service import \
    save_configuration_as_current
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_caching_in_solve_from_db(self):
        self.fill_db_with_patients_and_results()
        self.assertEqual(1, len(list(solve_from_db())))

    def test_solve_from_db(self):
        self.fill_db_with_patients_and_results()
        configuration = Configuration(
            manual_donor_recipient_scores=[
                ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=4, score=1.0)])
        save_configuration_as_current(configuration)
        self.assertEqual(1, len(list(solve_from_db())))

    def test_solve_from_db_multiple_countries(self):
        self.fill_db_with_patients(get_absolute_path('/tests/test_utilities/data2.xlsx'))
        configuration = Configuration(max_number_of_distinct_countries_in_round=1)
        save_configuration_as_current(configuration)
        solutions = list(solve_from_db())
        self.assertEqual(1, len(solutions))

    def test_solve_from_db_forbidden_countries(self):
        self.fill_db_with_patients(get_absolute_path('/tests/test_utilities/data3.xlsx'))
        configuration = Configuration(max_number_of_distinct_countries_in_round=3)
        save_configuration_as_current(configuration)
        solutions = list(solve_from_db())
        self.assertEqual(1, len(solutions))
