from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.patient_service import overwrite_patients_by_patients_from_excel, save_recipient, \
    save_donor
from txmatching.database.sql_alchemy_schema import RecipientModel, DonorModel
from txmatching.patients.patient import Recipient, RecipientRequirements, Donor
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_saving_patients_from_excel(self):
        patients = parse_excel_data(get_absolute_path("tests/test_utilities/data.xlsx"))
        overwrite_patients_by_patients_from_excel(patients)
        self.assertEqual(1, 1)

    def test_saving_patients(self):
        self.fill_db_with_patients_and_results()
        save_recipient(Recipient(
            acceptable_blood_groups=["A"],
            medical_id="TEST",
            recipient_requirements=RecipientRequirements(),
            related_donor_db_id=0,
            parameters=PatientParameters(blood_group="A", country_code="CZE"),
            db_id=1
        ))
        pat = RecipientModel.query.get(1)

        self.assertEqual("TEST", pat.medical_id)

    def test_saving_donors(self):
        self.fill_db_with_patients_and_results()
        save_donor(Donor(
            medical_id="TEST",
            related_recipient_db_id=1,
            parameters=PatientParameters(blood_group="A", country_code="CZE"),
            db_id=1
        ))
        pat = DonorModel.query.get(1)

        self.assertEqual("TEST", pat.medical_id)
