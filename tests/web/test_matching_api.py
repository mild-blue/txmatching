import dataclasses

from tests.test_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services import solver_service
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import HLAGroup, MatchTypes
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, MATCHING_NAMESPACE, TXM_EVENT_NAMESPACE


class TestSaveAndGetConfiguration(DbTests):

    def _get_split(self, split_code: str, broad_code: str = None):
        return {
            'display_code': split_code, 'high_res': None, 'split': split_code,
            'broad': broad_code if broad_code is not None else split_code
        }

    def test_get_matchings(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/resources/data.xlsx'))
        # TODO remove in https://github.com/mild-blue/txmatching/issues/372
        configuration = Configuration(
            require_compatible_blood_group=False,
            require_better_match_in_compatibility_index=False,
            require_better_match_in_compatibility_index_or_blood_group=False,
            max_number_of_distinct_countries_in_round=10
        )
        pairing_result = solve_from_configuration(configuration, get_txm_event_complete(txm_event_db_id))
        solver_service.save_pairing_result(pairing_result, 1)

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(configuration)

            res = client.post(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/{MATCHING_NAMESPACE}/calculate-for-config',
                json=conf_dto,
                headers=self.auth_headers
            )
            expected_antibodies = [{'antibody_matches': [],
                                    'hla_group': 'A'},
                                   {'antibody_matches': [{'hla_antibody': {'raw_code': 'B7', 'mfi': 8000, 'cutoff': 200, 'code': self._get_split('B7')},
                                                          'match_type': 'NONE'}],
                                    'hla_group': 'B'},
                                   {'antibody_matches': [],
                                    'hla_group': 'DRB1'},
                                   {'antibody_matches': [{'hla_antibody': {'raw_code': 'DQ5', 'mfi': 8000, 'cutoff': 2000, 'code': self._get_split('DQ5', 'DQ1')},
                                                          'match_type': 'NONE'},
                                                         {'hla_antibody': {'raw_code': 'DQ6', 'mfi': 8000, 'cutoff': 2000, 'code': self._get_split('DQ6', 'DQ1')},
                                                          'match_type': 'NONE'}],
                                    'hla_group': 'Other'}]

        expected_score = [
            {
                'hla_group': HLAGroup.A.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('A11'), 'raw_code': 'A11'},
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_type': {'code': self._get_split('A11'), 'raw_code': 'A11'},
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3'},
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3'},
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[0],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.B.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8'},
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8'},
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[1],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.DRB1.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                   'match_type': MatchTypes.SPLIT.name},
                                  {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                   'match_type': MatchTypes.SPLIT.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchTypes.SPLIT.name},
                                      {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchTypes.SPLIT.name}],
                'antibody_matches': expected_antibodies[2],
                'group_compatibility_index': 18.0
            },
            {
                'hla_group': HLAGroup.Other.name,
                'donor_matches': [],
                'recipient_matches': [],
                'group_compatibility_index': 0.0,
                'antibody_matches': expected_antibodies[3],
            },
        ]
        expected_score2 = [
            {
                'hla_group': HLAGroup.A.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('A2'), 'raw_code': 'A2'},
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_type': {'code': self._get_split('A2'), 'raw_code': 'A2'},
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3'},
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_type': {'code': self._get_split('A3'), 'raw_code': 'A3'},
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[0],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.B.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8'},
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_type': {'code': self._get_split('B8'), 'raw_code': 'B8'},
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_type': {'code': self._get_split('B7'), 'raw_code': 'B7'},
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[1],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.DRB1.name,
                'donor_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                   'match_type': MatchTypes.SPLIT.name},
                                  {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                   'match_type': MatchTypes.SPLIT.name}],
                'recipient_matches': [{'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchTypes.SPLIT.name},
                                      {'hla_type': {'code': self._get_split('DR11'), 'raw_code': 'DR11'},
                                       'match_type': MatchTypes.SPLIT.name}],
                'antibody_matches': expected_antibodies[2],
                'group_compatibility_index': 18.0
            },
            {
                'hla_group': HLAGroup.Other.name,
                'donor_matches': [],
                'recipient_matches': [],
                'antibody_matches': expected_antibodies[3],
                'group_compatibility_index': 0.0
            },
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
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][0][
                                 'detailed_score_per_group'][0][
                                 'donor_matches'
                             ])
        self.assertListEqual(expected_score2[0]['donor_matches'],
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][1][
                                 'detailed_score_per_group'][0][
                                 'donor_matches'
                             ])
        self.assertListEqual(expected_score[0]['recipient_matches'],
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][0][
                                 'detailed_score_per_group'][0][
                                 'recipient_matches'
                             ])
        self.assertListEqual(expected_score2[0]['recipient_matches'],
                             res.json['calculated_matchings'][0]['rounds'][0]['transplants'][1][
                                 'detailed_score_per_group'][0][
                                 'recipient_matches'
                             ])

    def test_correct_config_applied(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=1))

            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{MATCHING_NAMESPACE}/calculate-for-config',
                              json=conf_dto,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(9, res.json['found_matchings_count'])

            conf_dto2 = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=50))

            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{MATCHING_NAMESPACE}/calculate-for-config',
                              json=conf_dto2,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(947, res.json['found_matchings_count'])

    def test_solver_multiple_txm_events(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=1))

            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}/'
                              f'{MATCHING_NAMESPACE}/calculate-for-config',
                              json=conf_dto,
                              headers=self.auth_headers)
            self.assertEqual(9, res.json['found_matchings_count'])
            self.assertEqual(200, res.status_code)

            txm_event_db_id_2 = create_or_overwrite_txm_event(name='test2').db_id
            res = client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id_2}/'
                              f'{MATCHING_NAMESPACE}/calculate-for-config',
                              json=conf_dto,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(0, res.json['found_matchings_count'])
