import dataclasses

from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.config_service import \
    save_config_parameters_to_db
from txmatching.database.services.pairing_result_service import \
    solve_from_configuration_and_save
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.patients.hla_code import HLACode
from txmatching.utils.enums import (HLAAntibodyType, HLACrossmatchLevel,
                                    HLAGroup, MatchType, Solver)
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import (API_VERSION, CONFIGURATION_NAMESPACE,
                            MATCHING_NAMESPACE, TXM_EVENT_NAMESPACE)


class TestSaveAndGetConfiguration(DbTests):

    def _get_split(self, split_code: str, broad_code: str = None):
        hla_code = HLACode(
            high_res=None,
            split=split_code,
            broad=broad_code if broad_code is not None else split_code,
        )
        return {
            'high_res': hla_code.high_res,
            'split': hla_code.split,
            'broad': hla_code.broad
        }

    def test_get_matchings(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data.xlsx'))

        configuration_parameters = ConfigParameters(
            require_compatible_blood_group=False,
            require_better_match_in_compatibility_index=False,
            require_better_match_in_compatibility_index_or_blood_group=False,
            max_number_of_distinct_countries_in_round=10
        )

        configuration = save_config_parameters_to_db(config_parameters=configuration_parameters,
                                                     txm_event_id=txm_event_db_id,
                                                     user_id=1)

        solve_from_configuration_and_save(
            configuration=configuration,
            txm_event=get_txm_event_complete(txm_event_db_id)
        )

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(configuration_parameters)
            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{CONFIGURATION_NAMESPACE}/find-or-create-config',
                              json=conf_dto,
                              headers=self.auth_headers)

            config_id = res.json['config_id']
            res = client.get(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                f'{MATCHING_NAMESPACE}/calculate-for-config/{config_id}',
                headers=self.auth_headers
            )

            self.assertEqual(200, res.status_code)

            expected_antibodies = [{'antibody_matches': [],
                                    'hla_group': 'A'},
                                   {'antibody_matches': [{'hla_antibody': {'raw_code': 'B7', 'mfi': 8000, 'cutoff': 200,
                                                                           'code': self._get_split('B7')},
                                                          'match_type': 'NONE'}],
                                    'hla_group': 'B'},
                                   {'antibody_matches': [],
                                    'hla_group': 'DRB1'},
                                   {'antibody_matches': [{'hla_antibody': {'raw_code': 'DQ5', 'mfi': 8000,
                                                                           'cutoff': 2000,
                                                                           'second_raw_code': None,
                                                                           'second_code': None,
                                                                           'code': self._get_split('DQ5', 'DQ1'),
                                                                           'type': HLAAntibodyType.NORMAL},
                                                          'match_type': 'UNDECIDABLE'},
                                                         {'hla_antibody': {'raw_code': 'DQ6', 'mfi': 8000,
                                                                           'cutoff': 2000,
                                                                           'second_raw_code': None,
                                                                           'second_code': None,
                                                                           'code': self._get_split('DQ6', 'DQ1'),
                                                                           'type': HLAAntibodyType.NORMAL},
                                                          'match_type': 'UNDECIDABLE'}],
                                    'hla_group': 'DQ'}]

        expected_score = [
            {
                'hla_group': HLAGroup.A.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('A11'), 'raw_code': 'A11',
                                                'display_code': 'A11'},
                                   'match_type': MatchType.NONE.name},
                                  {'hla_type': {'code': self._get_split('A11'), 'raw_code': 'A11',
                                                'display_code': 'A11'},
                                   'match_type': MatchType.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3',
                                                    'display_code': 'A3'},
                                       'match_type': MatchType.NONE.name},
                                      {'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3',
                                                    'display_code': 'A3'},
                                       'match_type': MatchType.NONE.name}],
                'antibody_matches': expected_antibodies[0],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.B.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8',
                                                'display_code': 'B8'},
                                   'match_type': MatchType.NONE.name},
                                  {'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8',
                                                'display_code': 'B8'},
                                   'match_type': MatchType.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchType.NONE.name},
                                      {'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchType.NONE.name}],
                'antibody_matches': expected_antibodies[1],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.DRB1.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11',
                                                'display_code': 'DR11'},
                                   'match_type': MatchType.SPLIT.name},
                                  {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11',
                                                'display_code': 'DR11'},
                                   'match_type': MatchType.SPLIT.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchType.SPLIT.name},
                                      {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchType.SPLIT.name}],
                'antibody_matches': expected_antibodies[2],
                'group_compatibility_index': 18.0
            }
        ]
        expected_score2 = [
            {
                'hla_group': HLAGroup.A.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('A2'), 'raw_code': 'A2',
                                                'display_code': 'A2'},
                                   'match_type': MatchType.NONE.name},
                                  {'hla_type': {'code': self._get_split('A2'), 'raw_code': 'A2',
                                                'display_code': 'A2'},
                                   'match_type': MatchType.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3',
                                                    'display_code': 'A3'},
                                       'match_type': MatchType.NONE.name},
                                      {'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3',
                                                    'display_code': 'A3'},
                                       'match_type': MatchType.NONE.name}],
                'antibody_matches': expected_antibodies[0],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.B.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8',
                                                'display_code': 'B8'},
                                   'match_type': MatchType.NONE.name},
                                  {'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8',
                                                'display_code': 'B8'},
                                   'match_type': MatchType.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchType.NONE.name},
                                      {'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchType.NONE.name}],
                'antibody_matches': expected_antibodies[1],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.DRB1.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11',
                                                'display_code': 'DR11'},
                                   'match_type': MatchType.SPLIT.name},
                                  {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11',
                                                'display_code': 'DR11'},
                                   'match_type': MatchType.SPLIT.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchType.SPLIT.name},
                                      {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchType.SPLIT.name}],
                'antibody_matches': expected_antibodies[2],
                'group_compatibility_index': 18.0
            }
        ]
        # cannot be compared directly as we do not need to keep the order, but is left here as a reference
        expected = [
            {
                'order_id': 1,
                'score': 36.0,
                'rounds': [
                    {'transplants': [
                        {
                            'score': 18.0,
                            'detailed_score_per_group': expected_score,
                            'compatible_blood': True,
                            'donor': 'P21',
                            'recipient': 'P12'
                        },
                        {
                            'score': 18.0,
                            'detailed_score_per_group': expected_score2,
                            'compatible_blood': True,
                            'donor': 'P22',
                            'recipient': 'P11'
                        }
                    ]
                    }
                ],
                'countries': [
                    {
                        'country_code': 'CZE',
                        'donor_count': 2,
                        'recipient_count': 2
                    }
                ],
                'count_of_transplants': 2
            }
        ]

        self.maxDiff = None

        self.assertCountEqual(expected_antibodies[3]['antibody_matches'],
                              res.json['calculated_matchings'][0]['rounds'][0]['transplants'][1][
                                  'detailed_score_per_group'][3][
                                  'antibody_matches'])
        self.assertEqual(expected_antibodies[3]['hla_group'],
                         res.json['calculated_matchings'][0]['rounds'][0]['transplants'][1]['detailed_score_per_group'][
                             3]['hla_group'])

        self.assertListEqual(expected_score[0]['donor_matches'],
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][1][
                                 'detailed_score_per_group'][0][
                                 'donor_matches'
                             ])
        self.assertListEqual(expected_score2[0]['donor_matches'],
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][0][
                                 'detailed_score_per_group'][0][
                                 'donor_matches'
                             ])
        self.assertListEqual(expected_score[0]['recipient_matches'],
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][1][
                                 'detailed_score_per_group'][0][
                                 'recipient_matches'
                             ])
        self.assertListEqual(expected_score2[0]['recipient_matches'],
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][0][
                                 'detailed_score_per_group'][0][
                                 'recipient_matches'
                             ])

    def test_correct_config_applied(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                                           max_number_of_distinct_countries_in_round=1,
                                                           max_number_of_matchings=20,
                                                           max_matchings_in_all_solutions_solver=20))

            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{CONFIGURATION_NAMESPACE}/find-or-create-config',
                              json=conf_dto,
                              headers=self.auth_headers)

            config_id = res.json['config_id']
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{MATCHING_NAMESPACE}/calculate-for-config/{config_id}',
                             headers=self.auth_headers)

            self.assertEqual(200, res.status_code)
            self.assertEqual(9, len(res.json['calculated_matchings']))
            self.assertEqual(157, res.json['number_of_possible_transplants'])
            self.assertEqual(12, res.json['number_of_possible_recipients'])

            conf_dto2 = dataclasses.asdict(ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                                            max_number_of_distinct_countries_in_round=50,
                                                            hla_crossmatch_level=HLACrossmatchLevel.NONE,
                                                            max_number_of_matchings=20,
                                                            max_matchings_in_all_solutions_solver=20))

            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{CONFIGURATION_NAMESPACE}/find-or-create-config',
                              json=conf_dto2,
                              headers=self.auth_headers)

            config_id = res.json['config_id']
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{MATCHING_NAMESPACE}/calculate-for-config/{config_id}',
                             headers=self.auth_headers)

            self.assertEqual(200, res.status_code)
            self.assertEqual(20, len(res.json['calculated_matchings']))
            # should be the same as in the previous run as such configuration does not affect these counts
            self.assertEqual(157, res.json['number_of_possible_transplants'])
            self.assertEqual(12, res.json['number_of_possible_recipients'])

    def test_solver_multiple_txm_events(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                                           max_number_of_distinct_countries_in_round=1,
                                                           max_matchings_in_all_solutions_solver=20,
                                                           max_number_of_matchings=20))

            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{CONFIGURATION_NAMESPACE}/find-or-create-config',
                              json=conf_dto,
                              headers=self.auth_headers)

            config_id = res.json['config_id']
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                             f'{MATCHING_NAMESPACE}/calculate-for-config/{config_id}',
                             headers=self.auth_headers)
            self.assertEqual(9, len(res.json['calculated_matchings']))
            self.assertEqual(200, res.status_code)

            txm_event_db_id_2 = create_or_overwrite_txm_event(name='test2').db_id
            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id_2}/'
                              f'{CONFIGURATION_NAMESPACE}/find-or-create-config',
                              json=conf_dto,
                              headers=self.auth_headers)

            config_id = res.json['config_id']
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id_2}/'
                             f'{MATCHING_NAMESPACE}/calculate-for-config/{config_id}',
                             headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(0, len(res.json['calculated_matchings']))
            self.assertEqual(0, res.json['number_of_possible_transplants'])
            self.assertEqual(0, res.json['number_of_possible_recipients'])
