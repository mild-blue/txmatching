import json as jsonlib
from dataclasses import asdict
from pathlib import Path

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.patients.hla_model import HLATypeWithFrequencyRaw
from txmatching.utils.hla_system.hla_preparation_utils import \
    create_hla_type_with_frequency
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE

# txmatching/tests/resources/crossmatch_api_big_data_input.json
BIG_DATA_INPUT_JSON_PATH = (Path(__file__).parents[2].joinpath(
    Path('resources/crossmatch_api_big_data_input.json')))
# txmatching/tests/resources/crossmatch_api_big_data_output.json
BIG_DATA_OUTPUT_JSON_PATH = Path(__file__).parents[2].joinpath(
    Path('resources/crossmatch_api_big_data_output.json'))


class TestDoCrossmatchApi(DbTests):

    def test_do_crossmatch_api(self):
        # case: donor - HIGH_RES, recipient - HIGH_RES
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'A*02:02', 'is_frequent': True}],
                                           [{'hla_code': 'A*01:01', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2350,
                                      'name': 'A*02:02',
                                      'cutoff': 1000
                                      },
                                     {'mfi': 500,
                                      'name': 'A*01:01',
                                      'cutoff': 1000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertTrue(res.json['is_positive_crossmatch'])

            self.assertTrue(res.json['hla_to_antibody'][0]['is_positive_crossmatch'])
            self.assertEqual([{'hla_antibody': {'code': {'broad': 'A2', 'high_res': 'A*02:02', 'split': 'A2'},
                                                'cutoff': 1000, 'mfi': 2350, 'raw_code': 'A*02:02', 'second_code': None,
                                                'second_raw_code': None, 'type': 'NORMAL'}, 'match_type': 'HIGH_RES'}],
                             res.json['hla_to_antibody'][0]['antibody_matches'])
            self.assertFalse(res.json['hla_to_antibody'][1]['is_positive_crossmatch'])
            self.assertEqual([], res.json['hla_to_antibody'][1]['antibody_matches'])

            self.assertEqual(
                ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES,
                res.json['parsing_issues'][0]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][1]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][2]['parsing_issue_detail'])


        # case: no positive crossmatch
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'A*02:02', 'is_frequent': True}],
                                           [{'hla_code': 'A*01:01', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 500,
                                      'name': 'A*02:02',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 500,
                                      'name': 'A*01:01',
                                      'cutoff': 1000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertFalse(res.json['is_positive_crossmatch'])


    def test_do_crossmatch_api_with_ultra_high_res(self):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'A*02:02:01:02', 'is_frequent': True}],
                                           [{'hla_code': 'A*01:01:01:07', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2350,
                                      'name': 'A*02:02',
                                      'cutoff': 1000
                                      },
                                     {'mfi': 500,
                                      'name': 'A*01:01',
                                      'cutoff': 1000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertEqual(
                [{'hla_antibody': {'code': {'broad': 'A2', 'high_res': 'A*02:02', 'split': 'A2'},
                                   'cutoff': 1000, 'mfi': 2350, 'raw_code': 'A*02:02',
                                   'second_code': None,
                                   'second_raw_code': None, 'type': 'NORMAL'},
                  'match_type': 'HIGH_RES'}],
                res.json['hla_to_antibody'][0]['antibody_matches'])
            self.assertEqual([], res.json['hla_to_antibody'][1]['antibody_matches'])

            self.assertEqual(
                ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES,
                res.json['parsing_issues'][0]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][1]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][2]['parsing_issue_detail'])

    def test_do_crossmatch_api_with_different_code_formats(self):
        # case: donor - HIGH_RES, recipient - SPLIT
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'A*02:02', 'is_frequent': True}],
                                           [{'hla_code': 'A*01:01', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2350,
                                      'name': 'A2',
                                      'cutoff': 1000
                                      },
                                     {'mfi': 500,
                                      'name': 'A*01:01',
                                      'cutoff': 1000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertEqual(
                [{'hla_antibody': {'code': {'broad': 'A2', 'high_res': None, 'split': 'A2'},
                                   'cutoff': 1000, 'mfi': 2350, 'raw_code': 'A2',
                                   'second_code': None,
                                   'second_raw_code': None, 'type': 'NORMAL'},
                  'match_type': 'SPLIT'}],
                res.json['hla_to_antibody'][0]['antibody_matches'])
            self.assertEqual([], res.json['hla_to_antibody'][1]['antibody_matches'])

            self.assertEqual(
                ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                res.json['parsing_issues'][0]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][1]['parsing_issue_detail'])

        # case: donor - SPLIT, recipient - HIGH_RES
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'A2', 'is_frequent': True}],
                                           [{'hla_code': 'A*01:01', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2350,
                                      'name': 'A*02:02',
                                      'cutoff': 1000
                                      },
                                     {'mfi': 500,
                                      'name': 'A*01:01',
                                      'cutoff': 1000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertEqual(
                [{'hla_antibody': {'code': {'broad': 'A2', 'high_res': 'A*02:02', 'split': 'A2'},
                                   'cutoff': 1000, 'mfi': 2350, 'raw_code': 'A*02:02',
                                   'second_code': None,
                                   'second_raw_code': None, 'type': 'NORMAL'},
                  'match_type': 'SPLIT'}],
                res.json['hla_to_antibody'][0]['antibody_matches'])
            self.assertEqual([], res.json['hla_to_antibody'][1]['antibody_matches'])

            self.assertEqual(
                ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES,
                res.json['parsing_issues'][0]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][1]['parsing_issue_detail'])

        # CASE: donor has code that does not have a SPLIT level (NOT the only one in the list)
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPB1*218:01N', 'is_frequent': False},
                                            {'hla_code': 'DPB1*01:01', 'is_frequent': False}]],
            'recipient_antibodies': [],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            # here we will try to convert these infrequent potential HLA types from HIGH RES to split.
            # Due to the fact that the DPB1*218:01N code does not have a SPLIT level,
            # it won't fall into the assumed HLA types
            self.assertEqual(200, res.status_code)
            expected_assumed_hla_types = [
                asdict(create_hla_type_with_frequency(
                    HLATypeWithFrequencyRaw('DP1', is_frequent=True)
                ))]
            self.assertCountEqual(expected_assumed_hla_types,
                                  res.json['hla_to_antibody'][0]['assumed_hla_types'])

        # CASE: donor has code that does not have a SPLIT level (the only one in the list)
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPB1*218:01N', 'is_frequent': False}]],
            'recipient_antibodies': [],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            # here we will try to convert these infrequent potential HLA types from HIGH RES to split.
            # Due to the fact that the DPB1*218:01N code does not have a SPLIT level, and it's the only
            # one in the assumed hla types list, we leave it in high res as the lowest possible resolution
            self.assertEqual(200, res.status_code)
            expected_assumed_hla_types = [asdict(create_hla_type_with_frequency(
                HLATypeWithFrequencyRaw('DPB1*218:01N', is_frequent=False)
            ))]
            self.assertCountEqual(expected_assumed_hla_types,
                                  res.json['hla_to_antibody'][0]['assumed_hla_types'])

        # CASE: donor has unknown HIGH RES code according to our data
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'C*07:9999', 'is_frequent': False}]],
            'recipient_antibodies': [],
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            # since we don't know the SPLIT for this code, we'll leave HIGH RES,
            # but designate its frequency as the input
            self.assertEqual(200, res.status_code)
            expected_assumed_hla_types = [asdict(create_hla_type_with_frequency(
                HLATypeWithFrequencyRaw('C*07:9999', is_frequent=False)
            ))]
            self.assertCountEqual(expected_assumed_hla_types,
                                  res.json['hla_to_antibody'][0]['assumed_hla_types'])

        # CASE: donor has unknown code in unknown format according to our data
        json = {
            'potential_donor_hla_typing': [[{'hla_code': '921HLAUNKNWONFORMAT123', 'is_frequent': False}]],
            'recipient_antibodies': [],
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            expected_assumed_hla_types = [asdict(create_hla_type_with_frequency(
                HLATypeWithFrequencyRaw('921HLAUNKNWONFORMAT123', is_frequent=False)
            ))]
            self.assertCountEqual(expected_assumed_hla_types,
                                  res.json['hla_to_antibody'][0]['assumed_hla_types'])

    def test_theoretical_and_double_antibodies(self):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True}],
                                           [{'hla_code': 'DPB1*03:01', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*02:01', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DP[01:04,03:01]',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DP[02:02,02:01]',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 1000,
                                      'name': 'DP[01:04,04:01]',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 1000,
                                      'name': 'DP[01:03,03:01]',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 3000,
                                      'name': 'DP[02:01,01:01]',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 1000,
                                      'name': 'DP[02:01,01:01]',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertCountEqual([ParsingIssueDetail.CREATED_THEORETICAL_ANTIBODY,
                                   ParsingIssueDetail.CREATED_THEORETICAL_ANTIBODY,
                                   ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES,
                                   ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                                   ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                                   ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY],
                                  [parsing_issue['parsing_issue_detail'] for parsing_issue in
                                   res.json['parsing_issues']])
            double_antibody_match = {
                'hla_antibody': {'code': {'broad': 'DPA1', 'high_res': 'DPA1*01:04', 'split': 'DPA1'},
                                 'cutoff': 2000,
                                 'mfi': 2100,
                                 'raw_code': 'DPA1*01:04',
                                 'second_code': {'broad': 'DP3', 'high_res': 'DPB1*03:01', 'split': 'DP3'},
                                 'second_raw_code': 'DPB1*03:01', 'type': 'NORMAL'},
                'match_type': 'HIGH_RES'}
            theoretical_antibody_match = {
                'hla_antibody': {'code': {'broad': 'DPA2', 'high_res': 'DPA1*02:01', 'split': 'DPA2'},
                                 'cutoff': 2000,
                                 'mfi': 3000,
                                 'raw_code':
                                     'DPA1*02:01',
                                 'second_code': None,
                                 'second_raw_code': None,
                                 'type': 'THEORETICAL'},
                'match_type': 'THEORETICAL'}

            self.assertTrue(
                double_antibody_match in res.json['hla_to_antibody'][1]['antibody_matches'])
            self.assertTrue(
                double_antibody_match in res.json['hla_to_antibody'][2]['antibody_matches'])
            self.assertTrue(
                theoretical_antibody_match in res.json['hla_to_antibody'][3]['antibody_matches'])

    def test_theoretical_and_double_antibodies_equal_hlas_below_cutoff(self):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DQA1*01:01', 'is_frequent': True}],
                                           [{'hla_code': 'DQB1*02:02', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 100, 'name': 'DQ[01:01,02:02]', 'cutoff': 2000},
                                     {'mfi': 3000, 'name': 'DQ[01:01, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:02, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:01, 04:04]', 'cutoff': 2000}]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertNotIn({'hla_antibody':
                                  {'code': {'broad': 'DQA1',
                                            'high_res': 'DQA1*01:01',
                                            'split': 'DQA1'},
                                   'cutoff': 2000,
                                   'mfi': 3000,
                                   'raw_code': 'DQA1*01:01',
                                   'second_code': None,
                                   'second_raw_code': None,
                                   'type': 'THEORETICAL'},
                              'match_type': 'THEORETICAL'},
                             res.json['hla_to_antibody'][0]['antibody_matches'])

        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DQA1*01:01', 'is_frequent': True}],
                                           [{'hla_code': 'DQB1*02:02', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100, 'name': 'DQ[01:01,02:02]', 'cutoff': 2000},  # mfi >= cutoff
                                     {'mfi': 3000, 'name': 'DQ[01:01, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:02, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:01, 04:04]', 'cutoff': 2000}]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertIn({'hla_antibody':
                               {'code': {'broad': 'DQA1',
                                         'high_res': 'DQA1*01:01',
                                         'split': 'DQA1'},
                                'cutoff': 2000,
                                'mfi': 2550,
                                'raw_code': 'DQA1*01:01',
                                'second_code': None,
                                'second_raw_code': None,
                                'type': 'THEORETICAL'},
                           'match_type': 'THEORETICAL'},
                          res.json['hla_to_antibody'][0]['antibody_matches'])

        # case: double antibody is negative, because all positive representations are associated with other chains,
        # so there is no crossmatch
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DQA1*01:01', 'is_frequent': True},
                                            {'hla_code': 'DQA1*01:02', 'is_frequent': True}],
                                           [{'hla_code': 'DQB1*02:02', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 100, 'name': 'DQ[01:01, 02:02]', 'cutoff': 2000},
                                     {'mfi': 3000, 'name': 'DQ[01:01, 03:04]', 'cutoff': 2000},
                                     {'mfi': 4000, 'name': 'DQ[01:01, 02:33]', 'cutoff': 2000},
                                     {'mfi': 200, 'name': 'DQ[01:01, 04:04]', 'cutoff': 2000}]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            expected_summary = {'hla_code': {'broad': 'DQA1',
                                             'high_res': None,
                                             'split': 'DQA1'},
                                'mfi': 150,
                                'details_and_issues': ['NEGATIVE_ANTIBODY_IN_SUMMARY']}
            self.assertEqual(expected_summary, res.json['hla_to_antibody'][0]['summary'])

        # ULTRA HIGH RES
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DQA1*01:01:02:01', 'is_frequent': True}],
                                           [{'hla_code': 'DQB1*02:02', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 100, 'name': 'DQ[01:01, 02:02]', 'cutoff': 2000},
                                     {'mfi': 3000, 'name': 'DQ[01:01, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:02, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:01, 04:04]', 'cutoff': 2000}]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertNotIn({'hla_antibody':
                                  {'code': {'broad': 'DQA1',
                                            'high_res': 'DQA1*01:01',
                                            'split': 'DQA1'},
                                   'cutoff': 2000,
                                   'mfi': 3000,
                                   'raw_code': 'DQA1*01:01',
                                   'second_code': None,
                                   'second_raw_code': None,
                                   'type': 'THEORETICAL'},
                              'match_type': 'THEORETICAL'},
                             res.json['hla_to_antibody'][0]['antibody_matches'])

    def test_on_big_data(self):
        with open(BIG_DATA_INPUT_JSON_PATH, 'r') as file:
            json = jsonlib.load(file)
        with open(BIG_DATA_OUTPUT_JSON_PATH, 'r') as file:
            expected_json = jsonlib.load(file)
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            for res_match_for_hla_type, expected_match_for_hla_type \
                    in zip(res.json['hla_to_antibody'], expected_json['hla_to_antibody']):
                self.assertCountEqual(res_match_for_hla_type, expected_match_for_hla_type)
            self.assertCountEqual(res.json['parsing_issues'], expected_json['parsing_issues'])

    def test_with_integration_data(self):
        json = {
            'recipient_id': 'RID',
            'recipient_sample_id': 'R_SAMPLE_ID',
            'donor_code': 'DCODE',
            'donor_sample_id': 'D_SAMPLE_ID',
            'datetime': '2020-8-9T20:00:00.474Z',
            'potential_donor_hla_typing': [[{'hla_code': 'A*02:02', 'is_frequent': True}],
                                           [{'hla_code': 'A*01:01', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2350,
                                      'name': 'A*02:02',
                                      'cutoff': 1000
                                      },
                                     {'mfi': 500,
                                      'name': 'A*01:01',
                                      'cutoff': 1000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertEqual(json['recipient_id'], res.json['recipient_id'])
            self.assertEqual(json['recipient_sample_id'], res.json['recipient_sample_id'])
            self.assertEqual(json['donor_code'], res.json['donor_code'])
            self.assertEqual(json['donor_sample_id'], res.json['donor_sample_id'])
            self.assertEqual(json['datetime'], res.json['datetime'])
