from local_testing_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                                 populate_large_db,
                                                 populate_small_db)
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_excel
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_populate_small_db_works(self):
        populate_small_db()

    def test_populate_db_works_but_not_reupload_of_the_same_data(self):
        populate_large_db()
        patients = parse_excel_data(get_absolute_path(PATIENT_DATA_OBFUSCATED), country=None,
                                    txm_event_name='mock_data_CZE_CAN_IND')
        self.assertRaises(InvalidArgumentException, lambda: replace_or_add_patients_from_excel(patients))
        self.assertRaises(InvalidArgumentException, lambda: replace_or_add_patients_from_excel(patients))
