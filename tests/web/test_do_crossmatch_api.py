from dataclasses import asdict

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.utils.hla_system.hla_preparation_utils import create_hla_typing, create_hla_type
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE


class TestDoCrossmatchApi(DbTests):

    def test_do_crossmatch_api(self):
        # case: donor - HIGH_RES, recipient - HIGH_RES
        json = {
            "assumed_donor_hla_typing": [['A*02:02'], ['A*01:01']],
            "recipient_antibodies": [{'mfi': 2350,
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

    def test_do_crossmatch_api_with_different_code_formats(self):
        # case: donor - HIGH_RES, recipient - SPLIT
        json = {
            "assumed_donor_hla_typing": [['A*02:02'], ['A*01:01']],
            "recipient_antibodies": [{'mfi': 2350,
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
            "assumed_donor_hla_typing": [['A2'], ['A*01:01']],
            "recipient_antibodies": [{'mfi': 2350,
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
            "assumed_donor_hla_typing": ['DPA1*01:03', 'DPB1*03:01', 'DPA1*01:04', 'DPA1*02:01'],
            "recipient_antibodies": [{'mfi': 2100,
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
                                  [parsing_issue['parsing_issue_detail'] for parsing_issue in res.json['parsing_issues']])
            double_antibody_match = {'hla_antibody': {'code': {'broad': 'DPA1', 'high_res': 'DPA1*01:04', 'split': 'DPA1'},
                                                      'cutoff': 2000,
                                                      'mfi': 2100,
                                                      'raw_code': 'DPA1*01:04',
                                                      'second_code': {'broad': 'DP3', 'high_res': 'DPB1*03:01', 'split': 'DP3'},
                                                      'second_raw_code': 'DPB1*03:01', 'type': 'NORMAL'},
                                     'match_type': 'HIGH_RES'}
            theoretical_antibody_match = {'hla_antibody': {'code': {'broad': 'DPA2', 'high_res': 'DPA1*02:01', 'split': 'DPA2'},
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

    def test_do_crossmatch_for_assumed_hla_type(self):
        json = {
            "assumed_donor_hla_typing": [['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06'],
                                         ['DPA1*02:01'],
                                         ['DPA1*01:04']],
            "recipient_antibodies": [{'mfi': 2100,
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
            self.assertEqual(200, res.status_code)

            self.assertEqual(2, len(res.json['hla_to_antibody']))
            res_assumed_hla_typing = \
                [res.json['hla_to_antibody'][i]['hla_type']
                 for i in range(len(res.json['hla_to_antibody']))]
            expected_assumed_hla_typing = [[asdict(create_hla_type('DPA1*01:04'))],
                                           [asdict(create_hla_type('DPA1*02:01'))]]
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)
