import dataclasses

from tests.test_utilities.populate_db import create_or_overwrite_txm_event, PATIENT_DATA_OBFUSCATED
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.utils.enums import HLAGroup, MatchTypes
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, MATCHING_NAMESPACE, PATIENT_NAMESPACE


class TestSaveAndGetConfiguration(DbTests):

    def test_get_matchings(self):
        self.fill_db_with_patients(get_absolute_path('/tests/resources/data.xlsx'))

        with self.app.test_client() as client:
            conf_dto = dataclasses.asdict(Configuration(
                require_compatible_blood_group=False,
                require_better_match_in_compatibility_index=False,
                require_better_match_in_compatibility_index_or_blood_group=False,
                max_number_of_distinct_countries_in_round=10))

            res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config',
                              json=conf_dto,
                              headers=self.auth_headers)
            expected_antibodies = [{'antibody_matches': [],
                                    'hla_group': 'A'},
                                   {'antibody_matches': [{'hla_code': 'B7',
                                                          'match_type': 'NONE'}],
                                    'hla_group': 'B'},
                                   {'antibody_matches': [],
                                    'hla_group': 'DRB1'},
                                   {'antibody_matches': [{'hla_code': 'DQ5',
                                                          'match_type': 'NONE'},
                                                         {'hla_code': 'DQ6',
                                                          'match_type': 'NONE'}],
                                    'hla_group': 'Other'}]

        expected_score = [
            {
                'hla_group': HLAGroup.A.name,
                'donor_matches': [{'hla_code': 'A11',
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_code': 'A11',
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_code': 'A3',
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_code': 'A3',
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[0],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.B.name,
                'donor_matches': [{'hla_code': 'B8',
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_code': 'B8',
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_code': 'B7',
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_code': 'B7',
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[1],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.DRB1.name,
                'donor_matches': [{'hla_code': 'DR11',
                                   'match_type': MatchTypes.SPLIT.name},
                                  {'hla_code': 'DR11',
                                   'match_type': MatchTypes.SPLIT.name}],
                'recipient_matches': [{'hla_code': 'DR11',
                                       'match_type': MatchTypes.SPLIT.name},
                                      {'hla_code': 'DR11',
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
                'donor_matches': [{'hla_code': 'A2',
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_code': 'A2',
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_code': 'A3',
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_code': 'A3',
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[0],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.B.name,
                'donor_matches': [{'hla_code': 'B8',
                                   'match_type': MatchTypes.NONE.name},
                                  {'hla_code': 'B8',
                                   'match_type': MatchTypes.NONE.name}],
                'recipient_matches': [{'hla_code': 'B7',
                                       'match_type': MatchTypes.NONE.name},
                                      {'hla_code': 'B7',
                                       'match_type': MatchTypes.NONE.name}],
                'antibody_matches': expected_antibodies[1],
                'group_compatibility_index': 0.0
            },
            {
                'hla_group': HLAGroup.DRB1.name,
                'donor_matches': [{'hla_code': 'DR11',
                                   'match_type': MatchTypes.SPLIT.name},
                                  {'hla_code': 'DR11',
                                   'match_type': MatchTypes.SPLIT.name}],
                'recipient_matches': [{'hla_code': 'DR11',
                                       'match_type': MatchTypes.SPLIT.name},
                                      {'hla_code': 'DR11',
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

        self.assertCountEqual(expected_antibodies[3]["antibody_matches"],
                              res.json[0]["rounds"][0]["transplants"][1]['detailed_score_per_group'][3][
                                  "antibody_matches"])
        self.assertEqual(expected_antibodies[3]["hla_group"],
                         res.json[0]["rounds"][0]["transplants"][1]['detailed_score_per_group'][3]["hla_group"])

        self.assertListEqual(expected_score[0]['donor_matches'],
                             res.json[0]["rounds"][0]["transplants"][0]['detailed_score_per_group'][0][
                                 'donor_matches'
                             ])
        self.assertListEqual(expected_score2[0]['donor_matches'],
                             res.json[0]["rounds"][0]["transplants"][1]['detailed_score_per_group'][0][
                                 'donor_matches'
                             ])
        self.assertListEqual(expected_score[0]['recipient_matches'],
                             res.json[0]["rounds"][0]["transplants"][0]['detailed_score_per_group'][0][
                                 'recipient_matches'
                             ])
        self.assertListEqual(expected_score2[0]['recipient_matches'],
                             res.json[0]["rounds"][0]["transplants"][1]['detailed_score_per_group'][0][
                                 'recipient_matches'
                             ])


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
        res = client.put(f'{API_VERSION}/{PATIENT_NAMESPACE}/recipient', headers=self.auth_headers,
                         json=recipient_update_dict).json
        self.assertEqual(['A', 'AB'], res['acceptable_blood_groups'])
        recipients = client.get(f'{API_VERSION}/{PATIENT_NAMESPACE}', headers=self.auth_headers).json['recipients']
        self.assertEqual(recipient_update_dict['acceptable_blood_groups'], recipients[0]['acceptable_blood_groups'])

        self.assertIsNone(ConfigModel.query.get(1))


def test_correct_config_applied(self):
    self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))

    with self.app.test_client() as client:
        conf_dto = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=1))

        res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config',
                          json=conf_dto,
                          headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        self.assertEqual(9, len(res.json))

        conf_dto2 = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=50))

        res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config',
                          json=conf_dto2,
                          headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        self.assertEqual(503, len(res.json))


def test_solver_multiple_txm_events(self):
    self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))

    with self.app.test_client() as client:
        conf_dto = dataclasses.asdict(Configuration(max_number_of_distinct_countries_in_round=1))

        res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config',
                          json=conf_dto,
                          headers=self.auth_headers)
        self.assertEqual(200, res.status_code)

        create_or_overwrite_txm_event(name='test2')
        res = client.post(f'{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config',
                          json=conf_dto,
                          headers=self.auth_headers)
        self.assertEqual(200, res.status_code)
        self.assertEqual(0, len(res.json))
