import dataclasses

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.web import (API_VERSION, CONFIGURATION_NAMESPACE,
                            MATCHING_NAMESPACE, TXM_EVENT_NAMESPACE)


class TestPatientService(DbTests):

    def test_max_matchings_to_show_to_viewer_set_correctly(self):
        txm_event_db_id = self.fill_db_with_patients()

        self.assertEqual(0, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])

        config_parameters = ConfigParameters(max_matchings_to_show_to_viewer=10)
        first_config_id = self._calculate_for_config(config_parameters, txm_event_db_id)['config_id']
        self._set_default_config(first_config_id, txm_event_db_id)
        self.assertEqual(10, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])
        self.assertEqual(10, self._get_config(first_config_id, txm_event_db_id)['max_matchings_to_show_to_viewer'])

        config_parameters = ConfigParameters(max_matchings_to_show_to_viewer=2)
        second_config_id = self._calculate_for_config(config_parameters, txm_event_db_id)['config_id']
        self.assertNotEqual(first_config_id, second_config_id)
        self.assertEqual(10, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])
        self.assertEqual(2, self._get_config(second_config_id, txm_event_db_id)['max_matchings_to_show_to_viewer'])

        config_parameters = ConfigParameters(max_number_of_matchings=13)
        third_config_id = self._calculate_for_config(config_parameters, txm_event_db_id)['config_id']
        self._set_default_config(third_config_id, txm_event_db_id)
        self.assertEqual(0, self._get_config('default', txm_event_db_id)['max_matchings_to_show_to_viewer'])

    def test_correct_config_returned(self):
        txm_event_db_id = self.fill_db_with_patients()

        config_parameters_1 = ConfigParameters(use_high_resolution=True,
                                        max_number_of_matchings=20,
                                        solver_constructor_name=Solver.ILPSolver,
                                        hla_crossmatch_level=HLACrossmatchLevel.NONE)
        config_parameters_2 = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                        use_high_resolution=True,
                                        max_number_of_matchings=1000,
                                        max_debt_for_country=10,
                                        hla_crossmatch_level=HLACrossmatchLevel.NONE)

        config_1_id = self._find_config_id(config_parameters_1, txm_event_db_id)['config_id']
        config_2_id = self._find_config_id(config_parameters_2, txm_event_db_id)['config_id']

        config_parameters_1_return = self._get_config(config_1_id, txm_event_db_id)
        config_parameters_2_return = self._get_config(config_2_id, txm_event_db_id)

        self.assertEqual(config_parameters_1_return, dataclasses.asdict(config_parameters_1))
        self.assertEqual(config_parameters_2_return, dataclasses.asdict(config_parameters_2))

    def _calculate_for_config(self, configuration, txm_event_db_id):
        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(configuration)

        res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                          f'{CONFIGURATION_NAMESPACE}/find-config-id',
                          json=conf_dto,
                          headers=self.auth_headers)

        config_id = res.json['config_id']
        res = client.get(
            f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/{MATCHING_NAMESPACE}/'
            f'calculate-for-config/{config_id}',
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
