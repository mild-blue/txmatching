import dataclasses

from tests.test_utilities.prepare_app import DbTests
from txmatching.config.configuration import Configuration
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import matching_api, patient_api


class TestSaveAndGetConfiguration(DbTests):

    def test_get_matchings(self):
        self.fill_db_with_patients(get_absolute_path('/tests/test_utilities/data.xlsx'))
        self.api.add_namespace(matching_api, path='/matching')

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=10))

            res = client.post('/matching/calculate-for-config', json=conf_dto, headers=self.auth_headers)
            expected = [{'score': 36.0, 'rounds': [{'transplants': [
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P21', 'recipient': 'P12'},
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P22', 'recipient': 'P11'}]}],
                         'countries': [{'country_code': 'CZE', 'donor_count': 2, 'recipient_count': 2}]}]
            self.assertEqual(expected, res.json)

    def test_get_patients(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(patient_api, path='/pat')
        with self.app.test_client() as client:
            res = client.get('/pat/', headers=self.auth_headers)
            self.assertEqual(2, len(res.json["donors_dict"]))
            self.assertEqual(2, len(res.json["recipients_dict"]))

    def test_save_recipient(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(patient_api, path='/pat')
        recipient = {
            "db_id": 1,
            "acceptable_blood_groups": ["A"],
            "medical_id": "str",
            "parameters": {"blood_group": "A", "country_code": "CZE"},
            "related_donor_db_id": 0
        }
        with self.app.test_client() as client:
            val = client.put('/pat/recipient', headers=self.auth_headers, json=recipient).json["db_id"]
            recipients = client.get('/pat/', headers=self.auth_headers).json["recipients_dict"]
            self.assertEqual("str", recipients[str(val)]["medical_id"])
