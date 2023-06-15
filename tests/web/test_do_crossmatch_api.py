from dataclasses import asdict

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.patients.hla_model import HLATypeWithFrequencyRaw
from txmatching.utils.enums import AntibodyMatchTypes
from txmatching.utils.hla_system.hla_crossmatch import AntibodyMatch
from txmatching.utils.hla_system.hla_preparation_utils import (
    create_antibody_parsed, create_hla_type_with_frequency)
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE


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

            self.assertEqual([{'hla_antibody': {'code': {'broad': 'A2', 'high_res': 'A*02:02', 'split': 'A2'},
                                                'cutoff': 1000, 'mfi': 2350, 'raw_code': 'A*02:02', 'second_code': None,
                                                'second_raw_code': None, 'type': 'NORMAL'}, 'match_type': 'HIGH_RES'}],
                             res.json['hla_to_antibody'][0]['antibody_matches'])
            self.assertEqual([], res.json['hla_to_antibody'][1]['antibody_matches'])

            self.assertEqual(
                ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES,
                res.json['parsing_issues'][0]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][1]['parsing_issue_detail'])
            self.assertEqual(ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                             res.json['parsing_issues'][2]['parsing_issue_detail'])

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
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1', True)))],
                # corresponds to ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
                # potential HLA type at the input (no matched antibodies even in low res)
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

        # CASE: assumed hla type has several split/broad codes
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
            self.assertCountEqual(['DPA1', 'DPA2'], [code['hla_type']['code']['split'] for code in
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
            self.assertEqual('Multiple HLA codes in assumed HLA type are only accepted'
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
            res_parsing_issues = res.json['parsing_issues']
            expected_assumed_hla_typing = [
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:03', True))),
                 asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:06', True)))]
            ]
            self.assertFalse(ParsingIssueDetail.RARE_ALLELE_POSITIVE_CROSSMATCH.value in [
                parsing_issue['message'] for parsing_issue in res_parsing_issues
            ])
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
                                      }]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            res_assumed_hla_typing = [antibody_match['assumed_hla_types']
                                      for antibody_match in res.json['hla_to_antibody']]
            res_parsing_issues = res.json['parsing_issues']
            # Here, the code is evaluated as infrequent because the potential typing comprises a mix of
            # frequent and infrequent codes, and a crossmatch occurred only with the infrequent one.
            expected_assumed_hla_typing = [
                [asdict(create_hla_type_with_frequency(HLATypeWithFrequencyRaw('DPA1*01:04', False)))]
            ]
            self.assertTrue(ParsingIssueDetail.RARE_ALLELE_POSITIVE_CROSSMATCH.value in [
                parsing_issue['message'] for parsing_issue in res_parsing_issues
            ])
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

    def test_summary_antibody(self):
        # summary antibody is the antibody that is key for a given HLA type, thus having the highest MFI

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
        # so we expect DPA1*01:04 as summary antibody because it has the highest
        # mfi among matched antibodies (MFI DPA1*01:04 (2100) > MFI DPA1*01:05 (2050))
        expected_summary_antibody = {'hla_antibody':
                                         {'code': {'broad': 'DPA1',
                                                   'high_res': 'DPA1*01:04',
                                                   'split': 'DPA1'},
                                          'cutoff': 2000,
                                          'mfi': 2100,
                                          'raw_code': 'DPA1*01:04',
                                          'second_code': None,
                                          'second_raw_code': None,
                                          'type': 'NORMAL'},
                                     'match_type': 'HIGH_RES'}
        self.assertEqual(expected_summary_antibody, res.json['hla_to_antibody'][0]['summary_antibody'])

        # there are no matched antibodies to both antigen DPA1*02:01 and antigen DQA1*01:08
        for antibody_match_without_crossmatched_antibodies in res.json['hla_to_antibody'][1:]:
            self.assertCountEqual([], antibody_match_without_crossmatched_antibodies['antibody_matches'])
            # so the summary antibody should not be either (None value set)
            self.assertEqual(None, antibody_match_without_crossmatched_antibodies['summary_antibody'])

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
            res_summary_antibody = [antibody_match['summary_antibody']
                                    for antibody_match in res.json['hla_to_antibody']]
            expected_summary_antibody = AntibodyMatch(
                hla_antibody=create_antibody_parsed(
                    raw_code='DPA1*01:03',
                    mfi=2200,
                    cutoff=2000),
                match_type=AntibodyMatchTypes.HIGH_RES
            )
            self.assertEqual(res_summary_antibody, [asdict(expected_summary_antibody)])

        # CASE: mixed frequency without warning: summary antibody
        # has the highest MFI among frequent, but not among all
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:03',
                                      'cutoff': 2000
                                      },
                                     {'mfi': 4000,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      }],
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary_antibody = [antibody_match['summary_antibody']
                                    for antibody_match in res.json['hla_to_antibody']]
            # DPA1*01:04 has the highest MFI 4000, but this is a rather rare antibody,
            # so this crossmatch is better described by the DPA1*01:03
            # with the highest MFI among frequent antibodies:
            expected_summary_antibody = AntibodyMatch(
                hla_antibody=create_antibody_parsed(
                    raw_code='DPA1*01:03',
                    mfi=2100,
                    cutoff=2000),
                match_type=AntibodyMatchTypes.HIGH_RES
            )
            self.assertEqual(res_summary_antibody, [asdict(expected_summary_antibody)])

        # CASE: mixed frequency with warning
        json = {
            'potential_donor_hla_typing': [[{'hla_code': 'DPA1*01:03', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:06', 'is_frequent': True},
                                            {'hla_code': 'DPA1*01:04', 'is_frequent': False}]],
            'recipient_antibodies': [{'mfi': 2100,
                                      'name': 'DPA1*01:04',
                                      'cutoff': 2000
                                      }]
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            res_summary_antibody = [antibody_match['summary_antibody']
                                    for antibody_match in res.json['hla_to_antibody']]
            # When a crossmatch occurs with only infrequent codes, we leave the summary empty.
            self.assertEqual(res_summary_antibody, [None])
