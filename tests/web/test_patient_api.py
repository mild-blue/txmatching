import io

from tests.test_utilities.prepare_app import DbTests
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, PATIENT_NAMESPACE


class TestPatientService(DbTests):

    def test_get_patients(self):
        self.fill_db_with_patients(get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx'))
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{PATIENT_NAMESPACE}',
                             headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        for donor in res.json["donors"]:
            if donor["related_recipient_db_id"]:
                self.assertIn("detailed_score_with_related_recipient", donor)

    def test_upload_patients_via_file(self):
        with self.app.test_client() as client:
            data = {
                'file': (open(get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx'), 'rb'),
                         'patient_data_2020_07_obfuscated.xlsx')
            }
            res = client.put(f'{API_VERSION}/{PATIENT_NAMESPACE}/add-patients-file',
                             headers=self.auth_headers, data=data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(38, res.json["recipients_uploaded"])

    def test_upload_patients_via_invalid_file(self):
        with self.app.test_client() as client:
            data = {
                'file': (open(get_absolute_path('/tests/resources/test_file'), 'rb'),
                         'test_file')
            }
            res = client.put(f'{API_VERSION}/{PATIENT_NAMESPACE}/add-patients-file',
                             headers=self.auth_headers, data=data)

        self.assertEqual(400, res.status_code)
        self.assertEqual("Unexpected file format", res.json['message'])
