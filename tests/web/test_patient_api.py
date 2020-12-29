import os

from tests.test_utilities.populate_db import EDITOR_WITH_ONLY_ONE_COUNTRY, create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, PATIENT_NAMESPACE


class TestPatientService(DbTests):

    def test_get_patients(self):
        self.fill_db_with_patients(
            get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated_multi_country.xlsx'))
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{PATIENT_NAMESPACE}',
                             headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        for donor in res.json["donors"]:
            if donor["related_recipient_db_id"]:
                self.assertIn("detailed_score_with_related_recipient", donor)

    def test_upload_patients_via_file(self):
        res = self._upload_data()

        self.assertEqual(200, res.status_code)
        self.assertEqual(34, res.json["recipients_uploaded"])
        self.assertEqual(38, res.json["donors_uploaded"])

    def test_upload_patients_via_invalid_file(self):
        res = self._upload_data('/tests/resources/test_file')

        self.assertEqual(400, res.status_code)
        self.assertEqual("Unexpected file format", res.json['message'])

    def test_upload_patients_forbidden_country(self):
        self.login_with_credentials(EDITOR_WITH_ONLY_ONE_COUNTRY)
        res = self._upload_data()
        self.assertEqual(403, res.status_code)
        self.assertEqual("User with email editor_only_one_country@example.com does not have access to CAN!",
                         res.json["message"])

    def _upload_data(self, file='/tests/resources/patient_data_2020_07_obfuscated_multi_country.xlsx'):
        create_or_overwrite_txm_event(name="test")
        with self.app.test_client() as client:
            data = {
                'file': (open(get_absolute_path(file), 'rb'),
                         os.path.basename(file))
            }
            return client.put(f'{API_VERSION}/{PATIENT_NAMESPACE}/add-patients-file',
                              headers=self.auth_headers, data=data)
