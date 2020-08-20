from kidney_exchange.database.services.patient_service import save_patients
from kidney_exchange.utils.excel_parsing.parse_excel_data import parse_excel_data
from tests.test_utilities.prepare_app import DbTests


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_saving_patients(self):

        patients = parse_excel_data("test_utilities/data.xlsx")
        save_patients(patients)
