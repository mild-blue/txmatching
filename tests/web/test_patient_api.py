import os

from tests.test_utilities.populate_db import (EDITOR_WITH_ONLY_ONE_COUNTRY,
                                              PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.database.sql_alchemy_schema import UploadedFileModel
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, PATIENT_NAMESPACE, TXM_EVENT_NAMESPACE


class TestPatientService(DbTests):

    def test_get_patients(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/{PATIENT_NAMESPACE}',
                             headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        for donor in res.json['donors']:
            self.assertIn('detailed_score_with_related_recipient', donor)
            detailed_score_for_groups = donor['detailed_score_with_related_recipient']
            if donor['related_recipient_db_id']:
                pass
            else:
                for detailed_score_for_group in detailed_score_for_groups:
                    self.assertEqual(detailed_score_for_group['antibody_matches'], [])
                    self.assertEqual(detailed_score_for_group['recipient_matches'], [])
                    self.assertEqual(detailed_score_for_group['group_compatibility_index'], 0)

    def test_upload_patients_via_file(self):
        res = self._upload_data()

        self.assertEqual(200, res.status_code)
        self.assertEqual(34, res.json['recipients_uploaded'])
        self.assertEqual(38, res.json['donors_uploaded'])

        uploaded_files = UploadedFileModel.query.all()
        self.assertEqual(1, len(uploaded_files))
        self.assertEqual(os.path.basename(PATIENT_DATA_OBFUSCATED), uploaded_files[0].file_name)
        with open(get_absolute_path(PATIENT_DATA_OBFUSCATED), 'rb') as f:
            expected_uploaded_file = f.read()
        self.assertEqual(expected_uploaded_file, uploaded_files[0].file)

    def test_upload_patients_via_file_one_country(self):
        file_name = '/tests/resources/data.xlsx'
        res = self._upload_data(file_name)

        self.assertEqual(200, res.status_code)
        self.assertEqual(2, res.json['recipients_uploaded'])
        self.assertEqual(2, res.json['donors_uploaded'])

        uploaded_files = UploadedFileModel.query.all()
        self.assertEqual(1, len(uploaded_files))
        self.assertEqual(os.path.basename(file_name), uploaded_files[0].file_name)
        with open(get_absolute_path(file_name), 'rb') as f:
            expected_uploaded_file = f.read()
        self.assertEqual(expected_uploaded_file, uploaded_files[0].file)

    def test_upload_patients_via_invalid_file(self):
        res = self._upload_data('/tests/resources/test_file')

        self.assertEqual(400, res.status_code)
        self.assertEqual('Unexpected file format.', res.json['message'])

    def test_upload_patients_forbidden_country(self):
        self.login_with_credentials(EDITOR_WITH_ONLY_ONE_COUNTRY)
        res = self._upload_data()
        self.assertEqual(403, res.status_code)
        self.assertEqual('User with email editor_only_one_country@example.com does not have access to CAN!',
                         res.json['message'])

    def _upload_data(self, file=PATIENT_DATA_OBFUSCATED):
        txm_event_db_id = create_or_overwrite_txm_event(name='test').db_id
        with self.app.test_client() as client:
            data = {
                'file': (open(get_absolute_path(file), 'rb'),
                         os.path.basename(file))
            }
            return client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{PATIENT_NAMESPACE}/add-patients-file',
                              headers=self.auth_headers, data=data)
