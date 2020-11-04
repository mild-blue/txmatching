import dataclasses

from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import (API_VERSION, MATCHING_NAMESPACE, PATIENT_NAMESPACE,
                            patient_api)


class TestSaveAndGetConfiguration(DbTests):

    def test_get_matchings(self):
        self.fill_db_with_patients(get_absolute_path('/tests/resources/data.xlsx'))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(Configuration(
                require_compatible_blood_group=False,
                require_better_match_in_compatibility_index=False,
                require_better_match_in_compatibility_index_or_blood_group=False,
                max_number_of_distinct_countries_in_round=10))

            res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config', json=conf_dto,
                              headers=self.auth_headers)
            expected = [{'order_id': 1, 'score': 36.0, 'rounds': [{'transplants': [
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P21', 'recipient': 'P12'},
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P22', 'recipient': 'P11'}]}],
                         'countries': [{'country_code': 'CZE', 'donor_count': 2, 'recipient_count': 2}]}]
            self.assertEqual(expected, res.json)

    def test_get_patients(self):
        self.fill_db_with_patients()
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{PATIENT_NAMESPACE}', headers=self.auth_headers)
            self.assertEqual(2, len(res.json['donors']))
            self.assertEqual(2, len(res.json['recipients']))

    def test_save_recipient(self):
        self.fill_db_with_patients_and_results()
        recipient_update_dict = {
            'db_id': 1,
            'acceptable_blood_groups': ['A', 'AB'],
        }
        with self.app.test_client() as client:
            self.assertIsNotNone(ConfigModel.query.get(1))
            res = client.put(f'{API_VERSION}/{PATIENT_NAMESPACE}/recipient', headers=self.auth_headers, json=recipient_update_dict).json
            self.assertEqual(['A', 'AB'], res['acceptable_blood_groups'])
            recipients = client.get(f'{API_VERSION}/{PATIENT_NAMESPACE}', headers=self.auth_headers).json['recipients']
            self.assertEqual(recipient_update_dict['acceptable_blood_groups'], recipients[0]['acceptable_blood_groups'])

            self.assertIsNone(ConfigModel.query.get(1))

    def test_correct_config_applied(self):
        self.fill_db_with_patients(get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx'))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=1))

            res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config', json=conf_dto,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(9, len(res.json))

            conf_dto2 = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=50))

            res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config', json=conf_dto2,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(503, len(res.json))

    def test_solver_multiple_txm_events(self):
        self.fill_db_with_patients(get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx'))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=1))

            res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config', json=conf_dto,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            create_or_overwrite_txm_event(name='test2')
            res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config', json=conf_dto,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(0, len(res.json))
