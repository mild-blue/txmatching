import os

from tests.test_utilities.populate_db import (EDITOR_WITH_ONLY_ONE_COUNTRY,
                                              PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.txm_event_service import get_txm_event_all
from txmatching.database.sql_alchemy_schema import UploadedFileModel
from txmatching.patients.patient import DonorType
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

    def test_single_pair(self):
        txm_event_db_id = create_or_overwrite_txm_event(name='test').db_id
        donor_medical_id = 'donor_test'
        recipient_medical_id = 'recipient_test'
        with self.app.test_client() as client:
            json_data = {
                'donor': {
                    'medical_id': donor_medical_id,
                    'blood_group': 'A',
                    'hla_typing': [],
                    'donor_type': DonorType.DONOR.value,
                },
                'recipient': {
                    'medical_id': recipient_medical_id,
                    'acceptable_blood_groups': [],
                    'blood_group': 'A',
                    'hla_typing': [],
                    'recipient_cutoff': 2000,
                    'hla_antibodies': [],
                },
                'country_code': 'CZE'
            }
            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{PATIENT_NAMESPACE}/pairs',
                              headers=self.auth_headers, json=json_data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(1, res.json['recipients_uploaded'])
        self.assertEqual(1, res.json['donors_uploaded'])

        txm_event = get_txm_event_all(txm_event_db_id)

        self.assertEqual(donor_medical_id, txm_event.all_donors[0].medical_id)
        self.assertEqual(1, txm_event.all_donors[0].related_recipient_db_id)

    def test_invalid_cuttoff_values(self):
        txm_event_db_id = create_or_overwrite_txm_event(name='test').db_id
        donor_medical_id = 'donor_test'
        recipient_medical_id = 'recipient_test'
        with self.app.test_client() as client:
            json_data = {
                'donor': {
                    'medical_id': donor_medical_id,
                    'blood_group': 'A',
                    'hla_typing': [],
                    'donor_type': DonorType.DONOR.value,
                },
                'recipient': {
                    'medical_id': recipient_medical_id,
                    'acceptable_blood_groups': [],
                    'blood_group': 'A',
                    'hla_typing': [],
                    'recipient_cutoff': 2000,
                    'hla_antibodies': [{
                        'mfi': 2350,
                        'name': 'test',
                        'cutoff': 1000
                    },
                        {
                            'mfi': 2000,
                            'name': 'test',
                            'cutoff': 2000
                        }],
                },
                'country_code': 'CZE'
            }
            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{PATIENT_NAMESPACE}/pairs',
                              headers=self.auth_headers, json=json_data)

        self.assertEqual(400, res.status_code)
