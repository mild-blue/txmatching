from flask_restx import Api

from txmatching.config.configuration import Configuration
from txmatching.data_transfer_objects.configuration.configuration_to_dto import \
    configuration_to_dto
from txmatching.web import patient_api, matching_api
from tests.test_utilities.prepare_app import DbTests


class TestSaveAndGetConfiguration(DbTests):

    def test_get_matchings(self):
        api = Api(self.app)
        api.add_namespace(matching_api, path='/')

        with self.app.test_client() as client:
            conf_dto = configuration_to_dto(Configuration(
                enforce_compatible_blood_group=False,
                require_new_donor_having_better_match_in_compatibility_index=False,
                require_new_donor_having_better_match_in_compatibility_index_or_blood_group=False))

            res = client.post('/calculate-for-config', json=conf_dto)
            expected = [{'score': 36.0, 'rounds': [{'transplants': [
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P21', 'recipient': 'P12'},
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P22', 'recipient': 'P11'}]}],
                         'countries': [{'country_code': 'CZE', 'donor_count': 2, 'recipient_count': 2}]}]
            self.assertEqual(expected, res.json)

    def test_get_patients(self):
        api = Api(self.app)
        api.add_namespace(patient_api, path='/pat')
        with self.app.test_client() as client:
            res = client.get('/pat/')
            self.assertEqual(4, len(res.json))
