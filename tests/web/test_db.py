from tests.test_utilities.prepare_app import DbTests
from txmatching.config.configuration import Configuration, DonorRecipientScore
from txmatching.database.services.config_service import \
    save_configuration_as_current
from txmatching.solve_service.solve_from_db import solve_from_db


class TestSaveAndGetConfiguration(DbTests):

    def test_solve_from_db(self):
        self.fill_db_with_patients_and_results()
        configuration = Configuration(
            manual_donor_recipient_scores=[
                DonorRecipientScore(donor_id=1, recipient_id=4, score=1.0)],
            require_new_donor_having_better_match_in_compatibility_index=False)
        save_configuration_as_current(configuration)
        self.assertEqual(1, len(list(solve_from_db())))
