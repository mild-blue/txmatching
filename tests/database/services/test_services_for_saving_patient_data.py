import unittest

from txmatching.database.services.patient_service import save_patients
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app


class TestSolveFromDbAndItsSupportFunctionality(unittest.TestCase):
    def test_saving_patients(self):
        app = create_app()
        with app.app_context():
            patients = parse_excel_data("data/data.xlsx")
            save_patients(patients)
