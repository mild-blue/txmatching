import os

from sqlalchemy import and_

from local_testing_utilities.populate_db import (EDITOR_WITH_ONLY_ONE_COUNTRY,
                                                 PATIENT_DATA_OBFUSCATED)
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.hla_preparation_utils import (create_antibodies,
                                                        create_antibody,
                                                        create_hla_typing)
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.database.sql_alchemy_schema import (ConfigModel, DonorModel,
                                                    ParsingIssueModel,
                                                    RecipientModel,
                                                    UploadedFileModel)
from txmatching.patients.patient import DonorType, RecipientRequirements
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web import API_VERSION, PATIENT_NAMESPACE, TXM_EVENT_NAMESPACE


class TestPatientService(DbTests):

    def test_get_patients(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/configs/default',
                             headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        self.assertEqual(38, len(res.json['donors']))
        self.assertEqual(34, len(res.json['recipients']))
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
        self.assertEqual('TXM event 1 is not allowed for this user.',
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

        txm_event = get_txm_event_complete(txm_event_db_id)

        self.assertEqual(donor_medical_id, txm_event.all_donors[0].medical_id)
        self.assertEqual(1, txm_event.all_donors[0].related_recipient_db_id)

    def test_addition_of_bridging_donor(self):
        txm_event_db_id = create_or_overwrite_txm_event(name='test').db_id
        donor_medical_id = 'donor_test'
        with self.app.test_client() as client:
            json_data = {
                'donor': {
                    'medical_id': donor_medical_id,
                    'blood_group': 'A',
                    'hla_typing': [],
                    'donor_type': DonorType.BRIDGING_DONOR.value,
                },
                'country_code': 'CZE'
            }
            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{PATIENT_NAMESPACE}/pairs',
                              headers=self.auth_headers, json=json_data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(0, res.json['recipients_uploaded'])
        self.assertEqual(1, res.json['donors_uploaded'])

        txm_event = get_txm_event_complete(txm_event_db_id)

        self.assertEqual(donor_medical_id, txm_event.all_donors[0].medical_id)

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

            res_ = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{PATIENT_NAMESPACE}/configs/default',
                              headers=self.auth_headers)

        self.assertEqual(200, res.status_code)
        self.assertEqual(200, res_.status_code)

        self.assertEqual(0, len(res_.json['donors'][0]['all_messages']['warnings']))
        self.assertEqual(3, len(res_.json['donors'][0]['all_messages']['errors']))
        self.assertEqual(0, len(res_.json['recipients'][0]['all_messages']['warnings']))
        self.assertEqual(4, len(res_.json['recipients'][0]['all_messages']['errors']))

        parsing_issues = ParsingIssueModel.query.all()
        self.assertEqual(7, len(parsing_issues))
        self.assertEqual('TEST', parsing_issues[3].hla_code_or_group)
        self.assertEqual(
            ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY,
            parsing_issues[3].parsing_issue_detail
        )

    def test_donor_recipient_pair_deletion(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)
        self.assertEqual(len(txm_event.all_donors), 38)
        self.assertEqual(len(txm_event.all_recipients), 34)

        # Select donor and its recipient and check that they are in db
        donor_db_id = 10
        self.assertEqual(len([donor for donor in txm_event.all_donors if donor.db_id == donor_db_id]), 1)
        recipient_db_id = next(
            donor for donor in txm_event.all_donors if donor.db_id == donor_db_id).related_recipient_db_id
        self.assertEqual(
            len([recipient for recipient in txm_event.all_donors if recipient.db_id == recipient_db_id]),
            1
        )

        # Delete the donor-recipient pair
        with self.app.test_client() as client:
            res = client.delete(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                                f'{PATIENT_NAMESPACE}/pairs/{donor_db_id}',
                                headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.content_type)

        # Number of donors and recipients should decrease by 1
        txm_event = get_txm_event_complete(txm_event_db_id)
        self.assertEqual(len(txm_event.all_donors), 37)
        self.assertEqual(len(txm_event.all_recipients), 33)

        # The deleted donor and recipients are no longer in the db
        self.assertEqual(len([donor for donor in txm_event.all_donors if donor.db_id == donor_db_id]), 0)
        self.assertEqual(
            len([recipient for recipient in txm_event.all_donors if recipient.db_id == recipient_db_id]),
            0
        )

        # Second deletion should fail
        with self.app.test_client() as client:
            res = client.delete(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                                f'{PATIENT_NAMESPACE}/pairs/{donor_db_id}',
                                headers=self.auth_headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual('application/json', res.content_type)

    def test_update_donor(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        donor_db_id = 10
        etag = DonorModel.query.get(donor_db_id).etag

        # 1. update patient
        with self.app.test_client() as client:
            json_data = {
                'db_id': donor_db_id,
                'etag': etag,
                'blood_group': 'A',
                'hla_typing': {
                    'hla_types_list': [{'raw_code': 'A*01:02'},
                                       {'raw_code': 'B7'},
                                       {'raw_code': 'DR11'}]
                },
                'sex': 'M',
                'height': 200,
                'weight': 100,
                'year_of_birth': 1990,
                'active': True,
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/configs/default/donor',
                             headers=self.auth_headers, json=json_data)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.content_type)

        # Check that update was working
        txm_event = get_txm_event_complete(txm_event_db_id)
        donor = txm_event.active_and_valid_donors_dict[donor_db_id]
        self.assertEqual(donor.parameters.blood_group, BloodGroup.A)
        self.assertEqual(donor.parameters.hla_typing, create_hla_typing(['A*01:02', 'B7', 'DR11']))
        self.assertEqual(donor.parameters.sex, Sex.M)
        self.assertEqual(donor.parameters.height, 200)
        self.assertEqual(donor.parameters.weight, 100)
        self.assertEqual(donor.parameters.year_of_birth, 1990)
        self.assertEqual(donor.active, True)
        etag = DonorModel.query.get(donor_db_id).etag

        # 2. update with unspecified values
        with self.app.test_client() as client:
            json_data = {
                'db_id': donor_db_id,
                'etag': etag,
                'blood_group': 'B',
                'hla_typing': {
                    'hla_types_list': []
                },
                'active': False
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/configs/default/donor',
                             headers=self.auth_headers, json=json_data)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.content_type)

        # Check that update was working
        txm_event = get_txm_event_complete(txm_event_db_id)
        donor = next(donor for donor in txm_event.all_donors if donor.db_id == donor_db_id)

        self.assertEqual(donor.parameters.blood_group, BloodGroup.B)
        self.assertEqual(donor.parameters.hla_typing, create_hla_typing([]))
        self.assertEqual(donor.parameters.sex, None)
        self.assertEqual(donor.parameters.height, None)
        self.assertEqual(donor.parameters.weight, None)
        self.assertEqual(donor.parameters.year_of_birth, None)
        self.assertEqual(donor.active, False)

    def test_update_recipient(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        recipient_db_id = 10
        etag = RecipientModel.query.get(recipient_db_id).etag
        # 1. update patient
        with self.app.test_client() as client:
            json_data = {
                'db_id': recipient_db_id,
                'etag': etag,
                'blood_group': 'A',
                'hla_typing': {
                    'hla_types_list': []
                },
                'sex': 'M',
                'height': 200,
                'weight': 100,
                'year_of_birth': 1990,
                'acceptable_blood_groups': ['A', 'B', 'AB'],
                'hla_antibodies': {
                    'hla_antibodies_list': []
                },
                'recipient_requirements': {
                    'require_better_match_in_compatibility_index': True,
                    'require_better_match_in_compatibility_index_or_blood_group': True,
                    'require_compatible_blood_group': True
                },
                'cutoff': 42
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers, json=json_data)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.content_type)

        # Check that update was working
        txm_event = get_txm_event_complete(txm_event_db_id)
        recipient = next(recipient for recipient in txm_event.all_recipients if recipient.db_id == recipient_db_id)
        self.assertEqual(recipient.parameters.blood_group, BloodGroup.A)
        self.assertEqual(recipient.parameters.hla_typing, create_hla_typing([]))
        self.assertEqual(recipient.parameters.sex, Sex.M)
        self.assertEqual(recipient.parameters.height, 200)
        self.assertEqual(recipient.parameters.weight, 100)
        self.assertEqual(recipient.parameters.year_of_birth, 1990)
        # HACK: This should equal to [BloodGroup.A, BloodGroup.B, BloodGroup.AB]
        # TODO: https://github.com/mild-blue/txmatching/issues/477 represent blood as enum
        self.assertCountEqual(recipient.acceptable_blood_groups, ['A', 'B', 'AB'])
        self.assertEqual(recipient.hla_antibodies, create_antibodies([]))
        self.assertEqual(recipient.recipient_requirements, RecipientRequirements(True, True, True))
        self.assertEqual(recipient.recipient_cutoff, 42)

        etag = RecipientModel.query.get(recipient_db_id).etag
        # 2. update with unspecified values
        with self.app.test_client() as client:
            json_data = {
                'db_id': recipient_db_id,
                'etag': etag,
                'blood_group': 'B',
                'hla_typing': {
                    'hla_types_list': []
                },
                'acceptable_blood_groups': ['0'],
                'hla_antibodies': {
                    'hla_antibodies_list': []
                },
                'recipient_requirements': {
                    'require_better_match_in_compatibility_index': False,
                    'require_better_match_in_compatibility_index_or_blood_group': False,
                    'require_compatible_blood_group': False
                }
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers, json=json_data)
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.content_type)

        # Check that update was working
        txm_event = get_txm_event_complete(txm_event_db_id)
        recipient = next(recipient for recipient in txm_event.all_recipients if recipient.db_id == recipient_db_id)

        self.assertEqual(recipient.parameters.blood_group, BloodGroup.B)
        self.assertEqual(recipient.parameters.hla_typing, create_hla_typing([]))
        self.assertEqual(recipient.parameters.sex, None)
        self.assertEqual(recipient.parameters.height, None)
        self.assertEqual(recipient.parameters.weight, None)
        self.assertEqual(recipient.parameters.year_of_birth, None)
        # HACK: This should equal to [BloodGroup.ZERO]
        # TODO: https://github.com/mild-blue/txmatching/issues/477 represent blood as enum
        self.assertCountEqual(recipient.acceptable_blood_groups, ['0'])
        self.assertEqual(recipient.hla_antibodies, create_antibodies([]))
        self.assertEqual(recipient.recipient_requirements, RecipientRequirements(False, False, False))
        self.assertEqual(recipient.recipient_cutoff, 42)  # Cutoff is unchanged

    def test_save_recipient(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        recipient_db_id = 1
        etag = RecipientModel.query.get(recipient_db_id).etag
        recipient_update_dict = {
            'db_id': recipient_db_id,
            'acceptable_blood_groups': ['A', 'AB'],
            'etag': etag
        }
        with self.app.test_client() as client:
            self.assertIsNotNone(ConfigModel.query.get(recipient_db_id))
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers,
                             json=recipient_update_dict).json
            self.assertIsNotNone(ConfigModel.query.get(recipient_db_id))
            self.assertEqual(['A', 'AB'], res['recipient']['acceptable_blood_groups'])
            self.assertEqual([], res['parsing_issues'])
            recipients = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                                    f'{PATIENT_NAMESPACE}/configs/default',
                                    headers=self.auth_headers).json['recipients']
            self.assertEqual(recipient_update_dict['acceptable_blood_groups'], recipients[0]['acceptable_blood_groups'])

            # Config is not deleted
            self.assertIsNotNone(ConfigModel.query.get(recipient_db_id))

    def test_overriding_donor(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        donor_db_id = 10
        etag = DonorModel.query.get(donor_db_id).etag

        # 1. update patient
        with self.app.test_client() as client:
            json_data = {
                'db_id': donor_db_id,
                'etag': etag,
                'blood_group': 'A',
                'hla_typing': {
                    'hla_types_list': [{'raw_code': 'A*01:02'},
                                       {'raw_code': 'B7'},
                                       {'raw_code': 'DR11'}]
                },
                'sex': 'M',
                'height': 200,
                'weight': 100,
                'year_of_birth': 1990,
                'active': True,
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/configs/default/donor',
                             headers=self.auth_headers, json=json_data)
            self.assertEqual(200, res.status_code)

            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/configs/default/donor',
                             headers=self.auth_headers, json=json_data)
            self.assertEqual(406, res.status_code)

    def test_overriding_recipient(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        recipient_db_id = 10
        etag = RecipientModel.query.get(recipient_db_id).etag
        # 1. update patient
        with self.app.test_client() as client:
            json_data = {
                'db_id': recipient_db_id,
                'etag': etag,
                'blood_group': 'A',
                'hla_typing': {
                    'hla_types_list': []
                },
                'sex': 'M',
                'height': 200,
                'weight': 100,
                'year_of_birth': 1990,
                'acceptable_blood_groups': ['A', 'B', 'AB'],
                'hla_antibodies': {
                    'hla_antibodies_list': []
                },
                'recipient_requirements': {
                    'require_better_match_in_compatibility_index': True,
                    'require_better_match_in_compatibility_index_or_blood_group': True,
                    'require_compatible_blood_group': True
                },
                'cutoff': 42
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers, json=json_data)
            self.assertEqual(200, res.status_code)
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers, json=json_data)
            self.assertEqual(406, res.status_code)

    def test_sorted_antibodies(self):
        txm_event_db_id = create_or_overwrite_txm_event(name='test').db_id
        antibodies = [('B*08:01', 2350, 1000),
                      ('DPA1*02:20', 2350, 1000),
                      ('DPB1*09:01', 2350, 1000),
                      ('DPB1*895:01', 2350, 1000),
                      ('DQA1*05:07', 2350, 1000)]

        with self.app.test_client() as client:
            json_data = {
                'donor': {
                    'medical_id': 'donor_test',
                    'blood_group': 'A',
                    'hla_typing': [],
                    'donor_type': DonorType.DONOR.value
                },
                'recipient': {
                    'medical_id': 'recipient_test',
                    'acceptable_blood_groups': [],
                    'blood_group': 'A',
                    'hla_typing': [],
                    'recipient_cutoff': 2000,
                    'hla_antibodies':
                        [{'mfi': i[1], 'name': i[0], 'cutoff': i[2]} for i in reversed(antibodies)]
                },
                'country_code': 'CZE'
            }
            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{PATIENT_NAMESPACE}/pairs',
                              headers=self.auth_headers, json=json_data)
        self.assertEqual(200, res.status_code)

        expected_result_antibodies = create_antibodies([create_antibody(*i) for i in antibodies])

        txm_event = get_txm_event_complete(txm_event_db_id, True)
        recipient = txm_event.all_recipients[0]
        self.assertEqual(recipient.hla_antibodies, expected_result_antibodies)

        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/configs/default',
                             headers=self.auth_headers)
        self.assertEqual(200, res.status_code)

        for donor in res.json['donors']:
            antibodies_raw_codes = []
            expected_antibody_raw_codes = [antibody[0] for antibody in antibodies]
            for detailed_score_for_group in donor['detailed_score_with_related_recipient']:
                for antibody in detailed_score_for_group['antibody_matches']:
                    antibodies_raw_codes.append(antibody['hla_antibody']['raw_code'])
            self.assertEqual(antibodies_raw_codes, expected_antibody_raw_codes)

    def test_confirming_warning_issue(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        recipient_db_id = 10
        etag = RecipientModel.query.get(recipient_db_id).etag

        with self.app.test_client() as client:
            json_data = {
                'db_id': recipient_db_id,
                'etag': etag,
                'blood_group': 'A',
                'hla_typing': {
                    'hla_types_list': [{'raw_code': 'A*01:02'},
                                       {'raw_code': 'A*01:02'},
                                       {'raw_code': 'BW4'},
                                       {'raw_code': 'B7'},
                                       {'raw_code': 'DR11'}]
                },
                'sex': 'M',
                'height': 200,
                'weight': 100,
                'year_of_birth': 1990,
                'acceptable_blood_groups': ['A', 'B', 'AB'],
                'hla_antibodies': {
                    'hla_antibodies_list': []
                },
                'recipient_requirements': {
                    'require_better_match_in_compatibility_index': True,
                    'require_better_match_in_compatibility_index_or_blood_group': True,
                    'require_compatible_blood_group': True
                },
                'cutoff': 42
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers, json=json_data)
            self.assertEqual(200, res.status_code)

            warning_issue = ParsingIssueModel.query.filter(and_(ParsingIssueModel.recipient_id == recipient_db_id), (
                ParsingIssueModel.parsing_issue_detail == ParsingIssueDetail.IRRELEVANT_CODE)).first()


            self.assertEqual(None, warning_issue.confirmed_by)

            # TODO https://github.com/mild-blue/txmatching/issues/860
            # txm_event = get_txm_event_complete(txm_event_db_id)
            # self.assertFalse(recipient_db_id in txm_event.active_and_valid_recipients_dict)

            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/confirm-warning/{warning_issue.id}',
                             headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            txm_event = get_txm_event_complete(txm_event_db_id)
            self.assertTrue(recipient_db_id in txm_event.active_and_valid_recipients_dict)

            self.assertNotEqual(None, warning_issue.confirmed_by)

            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/confirm-warning/{warning_issue.id}',
                             headers=self.auth_headers)
            self.assertEqual(406, res.status_code)

    def test_confirming_error_issue(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        recipient_db_id = 10
        etag = RecipientModel.query.get(recipient_db_id).etag

        with self.app.test_client() as client:
            json_data = {
                'db_id': recipient_db_id,
                'etag': etag,
                'blood_group': 'A',
                'hla_typing': {
                    'hla_types_list': [{'raw_code': 'A*01:02'},
                                       {'raw_code': 'A*01:02'},
                                       {'raw_code': 'A*01:02'},
                                       {'raw_code': 'BW4'},
                                       {'raw_code': 'B7'},
                                       {'raw_code': 'DR11'}]
                },
                'sex': 'M',
                'height': 200,
                'weight': 100,
                'year_of_birth': 1990,
                'acceptable_blood_groups': ['A', 'B', 'AB'],
                'hla_antibodies': {
                    'hla_antibodies_list': []
                },
                'recipient_requirements': {
                    'require_better_match_in_compatibility_index': True,
                    'require_better_match_in_compatibility_index_or_blood_group': True,
                    'require_compatible_blood_group': True
                },
                'cutoff': 42
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers, json=json_data)
            self.assertEqual(200, res.status_code)

            error_issue = ParsingIssueModel.query.filter(and_(ParsingIssueModel.recipient_id == recipient_db_id), (
                ParsingIssueModel.parsing_issue_detail == ParsingIssueDetail.MORE_THAN_TWO_HLA_CODES_PER_GROUP)).first()

            self.assertEqual(None, error_issue.confirmed_by)

            txm_event = get_txm_event_complete(txm_event_db_id)
            self.assertFalse(recipient_db_id in txm_event.active_and_valid_recipients_dict)

            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/confirm-warning/{error_issue.id}',
                             headers=self.auth_headers)
            self.assertEqual(400, res.status_code)

            self.assertEqual(None, error_issue.confirmed_by)

    def test_unconfirming_warning_issue(self):
        txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        recipient_db_id = 10
        etag = RecipientModel.query.get(recipient_db_id).etag

        with self.app.test_client() as client:
            json_data = {
                'db_id': recipient_db_id,
                'etag': etag,
                'blood_group': 'A',
                'hla_typing': {
                    'hla_types_list': [{'raw_code': 'A*01:02'},
                                       {'raw_code': 'A*01:02'},
                                       {'raw_code': 'A*01:02'},
                                       {'raw_code': 'BW4'},
                                       {'raw_code': 'B7'},
                                       {'raw_code': 'DR11'}]
                },
                'sex': 'M',
                'height': 200,
                'weight': 100,
                'year_of_birth': 1990,
                'acceptable_blood_groups': ['A', 'B', 'AB'],
                'hla_antibodies': {
                    'hla_antibodies_list': []
                },
                'recipient_requirements': {
                    'require_better_match_in_compatibility_index': True,
                    'require_better_match_in_compatibility_index_or_blood_group': True,
                    'require_compatible_blood_group': True
                },
                'cutoff': 42
            }
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/recipient',
                             headers=self.auth_headers, json=json_data)
            self.assertEqual(200, res.status_code)

            warning_issue = ParsingIssueModel.query.filter(and_(ParsingIssueModel.recipient_id == recipient_db_id), (
                ParsingIssueModel.parsing_issue_detail == ParsingIssueDetail.IRRELEVANT_CODE)).first()
            self.assertEqual(None, warning_issue.confirmed_by)

            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/confirm-warning/{warning_issue.id}',
                             headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            txm_event = get_txm_event_complete(txm_event_db_id)
            self.assertFalse(recipient_db_id in txm_event.active_and_valid_recipients_dict)

            self.assertNotEqual(None, warning_issue.confirmed_by)

            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/unconfirm-warning/{warning_issue.id}',
                             headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertEqual(None, warning_issue.confirmed_by)

            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{PATIENT_NAMESPACE}/unconfirm-warning/{warning_issue.id}',
                             headers=self.auth_headers)
            self.assertEqual(406, res.status_code)

            self.assertFalse(recipient_db_id in txm_event.active_and_valid_recipients_dict)
