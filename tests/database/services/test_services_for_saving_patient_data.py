from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.patient_service import overwrite_patients_by_patients_from_excel
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_saving_patients(self):
        patients = parse_excel_data(get_absolute_path("tests/test_utilities/data.xlsx"))
        overwrite_patients_by_patients_from_excel(patients)
        self.assertEqual(1, 1)
