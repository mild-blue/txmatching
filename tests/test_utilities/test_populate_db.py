from tests.test_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                              populate_db)
from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_excel
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_populate_db_works_but_not_reupload_of_the_same_data(self):
        populate_db()
        patients = parse_excel_data(get_absolute_path(PATIENT_DATA_OBFUSCATED), country=None,
                                    txm_event_name='mock_data_CZE_CAN_IND')
        self.assertRaises(InvalidArgumentException, lambda: replace_or_add_patients_from_excel(patients))
