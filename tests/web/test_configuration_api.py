import dataclasses

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.web import (API_VERSION, CONFIGURATION_NAMESPACE,
                            MATCHING_NAMESPACE, TXM_EVENT_NAMESPACE)


class TestPatientService(DbTests):

    def test_max_matchings_to_show_to_viewer_set_correctly(self):
        txm_event_db_id = self.fill_db_with_patients()

        self.assertEqual(0, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])

        configuration = Configuration(max_matchings_to_show_to_viewer=10)
        first_config_id = self._calculate_for_config(configuration, txm_event_db_id)['config_id']
        self._set_default_config(first_config_id, txm_event_db_id)
        self.assertEqual(10, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])
        self.assertEqual(10, self._get_config(first_config_id, txm_event_db_id)['max_matchings_to_show_to_viewer'])

        configuration = Configuration(max_matchings_to_show_to_viewer=2)
        second_config_id = self._calculate_for_config(configuration, txm_event_db_id)['config_id']
        self.assertNotEqual(first_config_id, second_config_id)
        self.assertEqual(10, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])
        self.assertEqual(2, self._get_config(second_config_id, txm_event_db_id)['max_matchings_to_show_to_viewer'])

        configuration = Configuration(max_number_of_matchings=13)
        third_config_id = self._calculate_for_config(configuration, txm_event_db_id)['config_id']
        self._set_default_config(third_config_id, txm_event_db_id)
        self.assertEqual(0, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])

    def _calculate_for_config(self, configuration, txm_event_db_id):
        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(configuration)

        res = client.post(
            f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/{MATCHING_NAMESPACE}/calculate-for-config',
            json=conf_dto,
            headers=self.auth_headers
        )

        self.assertEqual(200, res.status_code)
        return res.json

    def _get_config(self, config_id, txm_event_db_id):
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{CONFIGURATION_NAMESPACE}/{config_id}',
                             headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
        return res.json

    def _set_default_config(self, config_id, txm_event_db_id):
        with self.app.test_client() as client:
            res = client.put(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{CONFIGURATION_NAMESPACE}/set-default',
                             json={'id': config_id},
                             headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
        return res.json
