import json as jsonlib
from dataclasses import asdict
from pathlib import Path

from tests.test_utilities.prepare_app_for_tests import DbTests
from tests.test_utilities.type_A_antibodies import type_A_antibodies
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLATypeWithFrequencyRaw
from txmatching.utils.hla_system.hla_cadaverous_crossmatch import (
    CadaverousCrossmatchDetailsIssues, CrossmatchSummary)
from txmatching.utils.hla_system.hla_preparation_utils import \
    create_hla_type_with_frequency
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE

# txmatching/tests/resources/crossmatch_api_big_data_input.json
BIG_DATA_INPUT_JSON_PATH = Path(__file__).parents[1].joinpath(
    Path('resources/crossmatch_api_big_data_input.json'))
# txmatching/tests/resources/crossmatch_api_big_data_output.json
BIG_DATA_OUTPUT_JSON_PATH = Path(__file__).parents[1].joinpath(
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

    def test_do_crossmatch_for_assumed_hla_types(self):
        # CASE: general case
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DQA1*02:01', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DQA1*02:01',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            res_assumed_hla_typing = [antibody_match['assumed_hla_types']
                                      for antibody_match in res.json['hla_to_antibody']]
            expected_assumed_hla_typing = [
                [
                    # for potential HLA type ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
                    # just DPA1*01:04 matches with recipients antibody, so we can determine the only
                    # one correct HLA type 'DPA1*01:04' from the given potential:
                    asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:04', True)))
                ],
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DQA1*02:01', True)))],
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:04', True)))]]
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: multiple matched antibodies for one hla type
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*02:01', 'is_frequent': True}],
                                           [{'hla_code': 'DQA1*01:08', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      }],
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertTrue(
                len(res.json['hla_to_antibody']) == len(json['potential_donor_hla_typing']))
            res_assumed_hla_typing = \
                [antibody_match['assumed_hla_types']
                 for antibody_match in res.json['hla_to_antibody']]
            # for potential HLA type ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
            # both antibodies 'DPA1*01:03' and 'DPA1*01:04' matches at the same time,
            # so we cannot determine the only one correct HLA type for this potential (leave both)
            expected_assumed_hla_type = [
                asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:03', True))),
                asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:04', True)))]
            self.assertCountEqual(expected_assumed_hla_type, res_assumed_hla_typing[0])

        # CASE: potential hla type without matched antibodies in high res
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*02:01', 'is_frequent': True}],
                                           [{'hla_code': 'DQA1*01:08', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:07',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DPA1*02:01',
                                      'cutoff': 2000
                                      }],
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertTrue(
                len(res.json['hla_to_antibody']) == len(json['potential_donor_hla_typing']))
            res_assumed_hla_typing = [antibody_match['assumed_hla_types']
                                      for antibody_match in res.json['hla_to_antibody']]
            expected_assumed_hla_typing = [
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1', True)))],
                # corresponds to ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
                # potential HLA type at the input (no matched antibodies in high res)
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DQA1*01:08', True)))],
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*02:01', True)))]]
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: potential hla type without matched antibodies even in low res
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*02:01', 'is_frequent': True}],
                                           [{'hla_code': 'DQA1*01:08', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DQA1*01:08',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DQA1*03:01',
                                      'cutoff': 2000
                                      }],
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertTrue(
                len(res.json['hla_to_antibody']) == len(json['potential_donor_hla_typing']))
            res_assumed_hla_typing = [antibody_match['assumed_hla_types']
                                      for antibody_match in res.json['hla_to_antibody']]
            # The expected results are no different from the results of the previous case.
            expected_assumed_hla_typing = [
                # corresponds to ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
                # potential HLA type at the input (no matched antibodies even in low res)
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1', True)))],
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DQA1*01:08', True)))],
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*02:01', True)))]]
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)
            # This means that we transfer assumed to split in all cases when we did not find
            # matches in high res, no matter if there are matches in low res or not

        # CASE: assumed hla type from antibodies below cutoff
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DQA1*02:01', 'is_frequent': True}],
                                           [{'hla_code': 'A*02:01', 'is_frequent': True},
                                            {'hla_code': 'A*02:02', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*01:04', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DQA1*02:01',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 500,
                                      'name': 'A*02:01',
                                      'cutoff': 2000}
                                     ]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            res_assumed_hla_typing = [antibody_match['assumed_hla_types']
                                      for antibody_match in res.json['hla_to_antibody']]
            expected_assumed_hla_typing = [
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:04', True)))],
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DQA1*02:01', True)))],
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:04', True)))],
                # was recognized by supportive HLA antibody with MFI below cutoff
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('A*02:01', True)))]
            ]
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: assumed hla type has several split/broad codes (with corresponding antibodies)
        json = {
            'potential_donor_hla_typing': [  # both splits DPA1 and DPA2 are presented here
                [{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                 {'hla_code': 'DPA1*02:06', 'is_frequent': True},
                 {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                [{'hla_code': 'DPA1*02:01', 'is_frequent': True}],
                [{'hla_code': 'DQA1*01:04', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DPA1*02:06',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DPA1*02:01',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            # so we successfully expect types in different not only HIGH RES, but also SPLIT levels
            # it's not a problem at all
            self.assertCountEqual(['DPA1', 'DPA2'], [code['hla_type']['code']['split'] for code in
                                                     res.json['hla_to_antibody'][0]['assumed_hla_types']])

        # CASE: assumed hla type has several split/broad codes (without corresponding antibodies)
        json = {
            'potential_donor_hla_typing': [  # both splits DPA1 and DPA2 are presented here
                [{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                 {'hla_code': 'DPA1*02:06', 'is_frequent': True},
                 {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                [{'hla_code': 'DPA1*02:01', 'is_frequent': True}],
                [{'hla_code': 'DQA1*01:04', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*02:01',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            # so even in a situation where we are converting assumed HLA types from HIGH RES to SPLIT,
            # having different SPLIT codes is ok (even though we do not allow such a situation directly on the input)
            self.assertCountEqual(['DPA1', 'DPA2'],
                                  [code['hla_type']['display_code'] for code in
                                   res.json['hla_to_antibody'][0]['assumed_hla_types']])

        # CASE: low res codes in assumed hla type
        json = {
            'potential_donor_hla_typing': [  # incorrect HLA type
                [{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                 {'hla_code': 'DPA1', 'is_frequent': True},
                 {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                [{'hla_code': 'DPA1*02:01', 'is_frequent': True}],
                [{'hla_code': 'DQA1*01:04', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DPA1*02:01',
                                      'cutoff': 2000
                                      }],
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(400, res.status_code)  # ValueError
            self.assertEqual('Multiple HLA codes in potential HLA types are only accepted'
                             ' in high resolution.',
                             res.json['message'])

        # CASE: only infrequent codes
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': False},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': False},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DQA1*02:01',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_assumed_hla_typing = [antibody_match['assumed_hla_types']
                                      for antibody_match in res.json['hla_to_antibody']]
            # This is evaluated as a frequent code because, in the event that all codes are infrequent,
            # we resort to their 'split'. The 'split' is always considered frequent.
            expected_assumed_hla_typing = [
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1', True)))]]
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: mixed frequency without warning
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2200,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DPA1*01:06',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            res_assumed_hla_typing = [antibody_match['assumed_hla_types']
                                      for antibody_match in res.json['hla_to_antibody']]
            res_crossmatch_issues = [issue for antibody_match in res.json['hla_to_antibody']
                                     for issue in antibody_match['summary']['details_and_issues']]
            expected_assumed_hla_typing = [
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:03', True))),
                 asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:06', True)))]
            ]
            self.assertFalse(CadaverousCrossmatchDetailsIssues.RARE_ALLELE_POSITIVE_CROSSMATCH
                             in res_crossmatch_issues)
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: mixed frequency with warning
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 100,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            res_assumed_hla_types = res.json['hla_to_antibody'][0]['assumed_hla_types']
            res_crossmatch_issues = [issue for antibody_match in res.json['hla_to_antibody']
                                     for issue in antibody_match['summary']['details_and_issues']]
            # Here, the code is evaluated as infrequent because the potential typing comprises a mix of
            # frequent and infrequent codes, and a crossmatch occurred only with the infrequent one.
            expected_assumed_hla_types = \
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:04', False))),
                 asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:03', True)))]
            self.assertTrue(CadaverousCrossmatchDetailsIssues.RARE_ALLELE_POSITIVE_CROSSMATCH
                            in res_crossmatch_issues)
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_types,
                                  res_assumed_hla_types)

    def test_summary(self):
        # CASE: The donor has several frequent HIGH RES codes that have the same
        #       SPLIT level in the assumed HLA types list:
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:05', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': True}],
                                           [{'hla_code': 'DPA1*02:01', 'is_frequent': True}],
                                           [{'hla_code': 'DQA1*01:08', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2050,
                                      'name': 'DPA1*01:05',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

        # assumed HLA type ['DPA1*01:04', 'DPA1*01:05'] matches both antibodies in the example
        self.assertCountEqual([
            {'hla_antibody': {
                'code': {'broad': 'DPA1',
                         'high_res': 'DPA1*01:04',
                         'split': 'DPA1'},
                'cutoff': 2000,
                'mfi': 2100,
                'raw_code': 'DPA1*01:04',
                'second_code': None,
                'second_raw_code': None,
                'type': 'NORMAL'},
                'match_type': 'HIGH_RES'},
            {'hla_antibody': {
                'code': {'broad': 'DPA1',
                         'high_res': 'DPA1*01:05',
                         'split': 'DPA1'},
                'cutoff': 2000,
                'mfi': 2050,
                'raw_code': 'DPA1*01:05',
                'second_code': None,
                'second_raw_code': None,
                'type': 'NORMAL'},
                'match_type': 'HIGH_RES'}],
            res.json['hla_to_antibody'][0]['antibody_matches'])
        # so we expect DPA1 as summary HLA code because donor has several frequent codes that crossmatch antibodies
        # summary MFI is an average of DPA1*01:04 (2100) and DPA1*01:05 (2050)
        expected_summary = CrossmatchSummary(
            hla_code=HLACode(broad='DPA1', high_res=None, split='DPA1'),
            mfi=2075,
            details_and_issues=[CadaverousCrossmatchDetailsIssues.MULTIPLE_HIGH_RES_MATCH,
                                CadaverousCrossmatchDetailsIssues.ANTIBODIES_MIGHT_NOT_BE_DSA]
        )
        self.assertEqual(asdict(expected_summary),
                         res.json['hla_to_antibody'][0]['summary'])

        # there are no matched antibodies to both antigen DPA1*02:01 and antigen DQA1*01:08,
        # summary should be found among negative antibodies. As this test example is not complete,
        # there are no corresponding negative antibodies and so the HLA type code is used as
        # the summary HLA code here. It is not expected to have no matched antibodies
        # in this case, but we test the correct summary nevertheless.
        for antibody_match_without_crossmatched_antibodies in res.json['hla_to_antibody'][1:]:
            self.assertCountEqual([], antibody_match_without_crossmatched_antibodies['antibody_matches'])
            expected_summary = CrossmatchSummary(
                hla_code=antibody_match_without_crossmatched_antibodies['assumed_hla_types'][0],
                mfi=None,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.NO_MATCHING_ANTIBODY]
            )
            self.assertCountEqual(
                asdict(expected_summary),
                antibody_match_without_crossmatched_antibodies['summary'])

        # CASE: The donor has several frequent HIGH RES codes that have the same
        #       SPLIT level in the assumed HLA types list (vol. 2):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2200,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'DPA1*01:06',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA1', high_res=None, split='DPA1'),
                mfi=2150,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.MULTIPLE_HIGH_RES_MATCH,
                                    CadaverousCrossmatchDetailsIssues.ANTIBODIES_MIGHT_NOT_BE_DSA]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The donor has several frequent HIGH RES codes that have the same
        #       SPLIT level in the assumed HLA types list, but only one positive crossmatch (vol. 3):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2200,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 100,
                                      'name': 'DPA1*01:06',
                                      'cutoff': 2000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA1', high_res='DPA1*01:03', split='DPA1'),
                mfi=2200,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.HIGH_RES_MATCH,
                                    CadaverousCrossmatchDetailsIssues.ANTIBODIES_MIGHT_NOT_BE_DSA]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: mixed frequency with warning
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 100,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summaries = [antibody_match['summary']
                             for antibody_match in res.json['hla_to_antibody']]
            # When a crossmatch occurs with only infrequent codes, we send issue unlikely crossmatch
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA1', high_res=None, split='DPA1'),
                mfi=2100,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.RARE_ALLELE_POSITIVE_CROSSMATCH]
            )
            self.assertEqual(res_summaries, [asdict(expected_summary)])

        # CASE: The donor has only one SPLIT HLA code in the assumed HLA types list (if all potential HLA types
        # are infrequent, they are parsed as single SPLIT HLA type):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': False},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': False},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 5000,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2000,
                                      'name': 'DPA1*01:06',
                                      'cutoff': 2000},
                                     {'mfi': 3000,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA1', high_res=None, split='DPA1'),
                mfi=3333,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.SPLIT_BROAD_MATCH]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The donor has only one SPLIT HLA code in the assumed HLA types list (if all potential HLA types
        # are infrequent, they are parsed as single SPLIT HLA type). The recipient is type A parsed (all antibodies
        # he is tested for are in high res and there are at least 20 of them). Assumed HLA type in this case is DPA1,
        # and all the antibodies that are DPA1 on SPLIT level are positive, this is therefore considered to be
        # HIGH_RES match. For better legibility, we use HIGH_RES_MATCH_ON_SPLIT_LEVEL message in crossmatch apiAd instead:
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': False},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': False},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 5000,
                                      'name': 'DPA1*01:05',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2000,
                                      'name': 'DPA1*01:02',
                                      'cutoff': 2000}] + type_A_antibodies
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA1', high_res=None, split='DPA1'),
                mfi=3500,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.HIGH_RES_MATCH_ON_SPLIT_LEVEL]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The donor has several SPLIT HLA codes in the assumed HLA types list:
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': False},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': False},
                                            {'hla_code': 'DPA1*02:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 5000,
                                      'name': 'DPA1*02:04',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2000,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000},
                                     {'mfi': 3000,
                                      'name': 'DPA1*01:06',
                                      'cutoff': 2000}] + type_A_antibodies
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA2', high_res=None, split='DPA2'),
                mfi=5000,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.HIGH_RES_MATCH_ON_SPLIT_LEVEL]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The donor has several frequent HIGH RES codes that have different
        # SPLIT levels in the assumed HLA types list (all above cutoff):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'B*07:02', 'is_frequent': True},
                                            {'hla_code': 'B*08:01', 'is_frequent': True},
                                            {'hla_code': 'B*08:02', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 3000,
                                      'name': 'B*07:02',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 1990,
                                      'name': 'B*08:01',
                                      'cutoff': 2000},
                                     {'mfi': 2500,
                                      'name': 'B*08:02',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='B7', high_res=None, split='B7'),
                mfi=3000,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.MULTIPLE_HIGH_RES_MATCH,
                                    CadaverousCrossmatchDetailsIssues.ANTIBODIES_MIGHT_NOT_BE_DSA]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The donor has several frequent HIGH RES codes that have different
        # SPLIT levels in the assumed HLA types list (all above cutoff):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'B*07:02', 'is_frequent': True},
                                            {'hla_code': 'B*08:01', 'is_frequent': True},
                                            {'hla_code': 'B*08:02', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 3000,
                                      'name': 'B*07:02',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 2100,
                                      'name': 'B*08:01',
                                      'cutoff': 2000},
                                     {'mfi': 2500,
                                      'name': 'B*08:02',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='B7', high_res=None, split='B7'),
                mfi=3000,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.MULTIPLE_HIGH_RES_MATCH,
                                    CadaverousCrossmatchDetailsIssues.AMBIGUITY_IN_HLA_TYPIZATION]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The donor has the only one HIGH RES HLA codes in the assumed HLA types list,
        # and at the same time it is frequent and has MFI ABOVE cutoff:
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 2000,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA1', high_res='DPA1*01:03', split='DPA1'),
                mfi=2000,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.HIGH_RES_MATCH]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The donor has the only HIGH RES HLA code(s) in the assumed HLA types list,
        # and at the same time it is frequent and has MFI BELOW cutoff:
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 1000,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='DPA1', high_res=None, split='DPA1'),
                mfi=1000,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.NEGATIVE_ANTIBODY_IN_SUMMARY]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The recipient doesn't have any crossmatched antibodies against donor's assumed hla types (1):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'B*07:04', 'is_frequent': True},
                                            {'hla_code': 'B*07:05', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 1500,
                                      'name': 'B*07:04',
                                      'cutoff': 2000},
                                     {'mfi': 1000,
                                      'name': 'B*07:05',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='B7', high_res=None, split='B7'),
                mfi=1500,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.NEGATIVE_ANTIBODY_IN_SUMMARY]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The recipient doesn't have any crossmatched antibodies against donor's assumed hla types (2):
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'B7', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 1500,
                                      'name': 'B*07:04',
                                      'cutoff': 2000},
                                     {'mfi': 1000,
                                      'name': 'B*07:05',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='B7', high_res=None, split='B7'),
                mfi=1500,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.NEGATIVE_ANTIBODY_IN_SUMMARY]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

        # CASE: The recipient has no antibodies that match with the donor's assumed hla types:
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'A*01:01N', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 1000,
                                      'name': 'A*01:01',
                                      'cutoff': 3000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad=None, high_res='A*01:01N', split=None),
                mfi=None,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.NO_MATCHING_ANTIBODY]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])


        # CASE: donor - HIGH RES vs. recipient - SPLIT
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'A*01:01', 'is_frequent': True},
                                            {'hla_code': 'A*02:01', 'is_frequent': True},
                                            {'hla_code': 'A*02:02', 'is_frequent': True}]],
            'recipient_antibodies': [{'mfi': 3000,
                                      'name': 'A2',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 100,
                                      'name': 'A*01:01',
                                      'cutoff': 2000}]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary = [antibody_match['summary']
                           for antibody_match in res.json['hla_to_antibody']]
            expected_summary = CrossmatchSummary(
                hla_code=HLACode(broad='A2', high_res=None, split='A2'),
                mfi=3000,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.SPLIT_BROAD_MATCH,
                                    CadaverousCrossmatchDetailsIssues.ANTIBODIES_MIGHT_NOT_BE_DSA]
            )
            self.assertEqual(res_summary, [asdict(expected_summary)])

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
