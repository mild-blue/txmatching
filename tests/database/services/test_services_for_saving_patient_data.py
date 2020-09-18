from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services import txm_event_service
from txmatching.database.services.patient_service import (
    save_patients_from_excel_to_empty_txm_event, update_donor,
    update_recipient)
from txmatching.database.sql_alchemy_schema import DonorModel, RecipientModel
from txmatching.patients.patient import Donor, Recipient, RecipientRequirements
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.country import Country
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_saving_patients_from_excel(self):
        patients = parse_excel_data(get_absolute_path('tests/test_utilities/data.xlsx'))
        txm_event = txm_event_service.create_or_overwrite_txm_event('test')
        save_patients_from_excel_to_empty_txm_event(patients, txm_event.db_id)
        self.assertEqual(1, 1)

    def test_saving_patients(self):
        self.fill_db_with_patients_and_results()
        update_recipient(Recipient(
            acceptable_blood_groups=['A'],
            medical_id='TEST',
            recipient_requirements=RecipientRequirements(),
            related_donor_db_id=0,
            parameters=PatientParameters(blood_group='A', country_code=Country.CZE),
            db_id=1
        ))
        pat = RecipientModel.query.get(1)

        self.assertEqual('TEST', pat.medical_id)

    def test_saving_donors(self):
        self.fill_db_with_patients_and_results()
        update_donor(Donor(
            medical_id='TEST',
            related_recipient_db_id=1,
            parameters=PatientParameters(blood_group='A', country_code=Country.CZE),
            db_id=1
        ))
        pat = DonorModel.query.get(1)

        self.assertEqual('TEST', pat.medical_id)
