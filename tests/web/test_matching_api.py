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
            conf_dto = dataclasses.asdict(Configuration(
                enforce_compatible_blood_group=False,
                require_new_donor_having_better_match_in_compatibility_index=False,
                require_new_donor_having_better_match_in_compatibility_index_or_blood_group=False))

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
            self.assertEqual(2, len(res.json["donors"]))
            self.assertEqual(2, len(res.json["recipients"]))
