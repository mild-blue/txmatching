from dataclasses import asdict

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.utils.hla_system.hla_preparation_utils import create_hla_type
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE


class TestDoCrossmatchApi(DbTests):

    def test_do_crossmatch_api(self):
        # case: donor - HIGH_RES, recipient - HIGH_RES
        json = {
            "potential_donor_hla_typing": [['A*02:02'], ['A*01:01']],
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

    def test_do_crossmatch_api_with_ultra_high_res(self):
        json = {
            "potential_donor_hla_typing": [['A*02:02:01:02'], ['A*01:01:01:07']],
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
            "potential_donor_hla_typing": [['A*02:02'], ['A*01:01']],
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
            "potential_donor_hla_typing": [['A2'], ['A*01:01']],
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
            "potential_donor_hla_typing": [['DPA1*01:03'], ['DPB1*03:01'], ['DPA1*01:04'],
                                           ['DPA1*02:01']],
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

    def test_theoretical_and_double_antibodies_equal_hlas_below_cutoff(self):
        json = {
            "potential_donor_hla_typing": [['DQA1*01:01'], ['DQB1*03:03'], ['A*02:02']],
            "recipient_antibodies": [{'mfi': 100, 'name': 'DQ[01:01,02:02]', 'cutoff': 2000},
                                     {'mfi': 3000, 'name': 'DQ[01:01, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:02, 03:03]', 'cutoff': 2000},
                                     {'mfi': 100, 'name': 'DQ[01:01, 04:04]', 'cutoff': 2000},
                                     {'mfi': 2100, 'name': 'A*02:02', 'cutoff': 2000}]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertEqual([{'hla_antibody': {'code': {'broad': 'A2', 'high_res': 'A*02:02', 'split': 'A2'},
                                                'cutoff': 2000, 'mfi': 2100, 'raw_code': 'A*02:02', 'second_code': None,
                                                'second_raw_code': None, 'type': 'NORMAL'}, 'match_type': 'HIGH_RES'}],
                             res.json['hla_to_antibody'][0]['antibody_matches'])

    def test_do_crossmatch_for_assumed_hla_types(self):
        # CASE: general case
        json = {
            "potential_donor_hla_typing": [['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06'],
                                           ['DQA1*02:01'],
                                           ['DPA1*01:04']],
            "recipient_antibodies": [{'mfi': 2100,
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

            res_assumed_hla_typing = [antibody_match['assumed_hla_type']
                                      for antibody_match in res.json['hla_to_antibody']]
            expected_assumed_hla_typing = [
                [
                # for potential HLA type ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
                # just DPA1*01:04 matches with recipients antibody, so we can determine the only
                # one correct HLA type 'DPA1*01:04' from the given potential:
                asdict(create_hla_type('DPA1*01:04'))
                ],
                [asdict(create_hla_type('DQA1*02:01'))],
                [asdict(create_hla_type('DPA1*01:04'))]]
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: multiple matched antibodies for one hla type
        json = {
            "potential_donor_hla_typing": [['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06'],
                                           ['DPA1*02:01'],
                                           ['DQA1*01:08']],
            "recipient_antibodies": [{'mfi': 2100,
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
                [antibody_match['assumed_hla_type']
                 for antibody_match in res.json['hla_to_antibody']]
            # for potential HLA type ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
            # both antibodies 'DPA1*01:03' and 'DPA1*01:04' matches at the same time,
            # so we cannot determine the only one correct HLA type for this potential (leave both)
            expected_assumed_hla_type = [asdict(create_hla_type('DPA1*01:03')),
                                         asdict(create_hla_type('DPA1*01:04'))]
            self.assertCountEqual(expected_assumed_hla_type, res_assumed_hla_typing[0])

        # CASE: potential hla type without matched antibodies in high res
        json = {
            "potential_donor_hla_typing": [['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06'],
                                           ['DPA1*02:01'],
                                           ['DQA1*01:08']],
            "recipient_antibodies": [{'mfi': 2100,
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
            res_assumed_hla_typing = [antibody_match['assumed_hla_type']
                                      for antibody_match in res.json['hla_to_antibody']]
            expected_assumed_hla_typing = [
                [asdict(create_hla_type('DPA1'))],  # corresponds to ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
                                                    # potential HLA type at the input (no matched antibodies in high res)
                [asdict(create_hla_type('DQA1*01:08'))],
                [asdict(create_hla_type('DPA1*02:01'))]]
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: potential hla type without matched antibodies even in low res
        json = {
            "potential_donor_hla_typing": [['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06'],
                                           ['DPA1*02:01'],
                                           ['DQA1*01:08']],
            "recipient_antibodies": [{'mfi': 2100,
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
            res_assumed_hla_typing = [antibody_match['assumed_hla_type']
                                      for antibody_match in res.json['hla_to_antibody']]
            # The expected results are no different from the results of the previous case.
            expected_assumed_hla_typing = [
                [asdict(create_hla_type('DPA1'))],  # corresponds to ['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06']
                                                    # potential HLA type at the input (no matched antibodies even in low res)
                [asdict(create_hla_type('DQA1*01:08'))],
                [asdict(create_hla_type('DPA1*02:01'))]]
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)
            # This means that we transfer assumed to split in all cases when we did not find
            # matches in high res, no matter if there are matches in low res or not

        # CASE: assumed hla type from antibodies below cutoff
        json = {
            "potential_donor_hla_typing": [['DPA1*01:03', 'DPA1*01:04', 'DPA1*01:06'],
                                           ['DQA1*02:01'],
                                           ['DPA1*01:04'],
                                           ['A*02:01', 'A*02:02']],
            "recipient_antibodies": [{'mfi': 2100,
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

            res_assumed_hla_typing = [antibody_match['assumed_hla_type']
                                      for antibody_match in res.json['hla_to_antibody']]
            expected_assumed_hla_typing = [
                [asdict(create_hla_type('DPA1*01:04'))],
                [asdict(create_hla_type('DQA1*02:01'))],
                [asdict(create_hla_type('DPA1*01:04'))],
                [asdict(create_hla_type('A*02:01'))]  # was recognized by supportive HLA antibody with MFI below cutoff
            ]
            self.assertTrue(len(res_assumed_hla_typing) == len(json['potential_donor_hla_typing']))
            self.assertCountEqual(expected_assumed_hla_typing,
                                  res_assumed_hla_typing)

        # CASE: assumed hla type has several split/broad codes
        json = {
            "potential_donor_hla_typing": [
                ['DPA1*01:03', 'DPA1*01:04', 'DPA1*02:06'],  # both splits DPA1 and DPA2 are presented here
                ['DPA1*02:01'],
                ['DQA1*01:04']],
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
            self.assertEqual(400, res.status_code)  # ValueError
            self.assertEqual("Assumed HLA type must be uniquely defined in "
                             "split or broad resolution.",
                             res.json['message'])

        # CASE: low res codes in assumed hla type
        json = {
            "assumed_donor_hla_typing": [['DPA1*01:03', 'DPA1*01:04', 'DPA1'],  # incorrect HLA type
                                         ['DPA1*02:01'],
                                         ['DQA1*01:04']],
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
            self.assertEqual(400, res.status_code)  # ValueError
            self.assertEqual('Multiple HLA codes in assumed HLA type are only accepted'
                             ' in high resolution.',
                             res.json['message'])

    def test_summary_antibody(self):
        # summary antibody is the antibody that is key for a given HLA type, thus having the highest MFI

        json = {
            "potential_donor_hla_typing": [['DPA1*01:04', 'DPA1*01:05', 'DPA1*01:06'],
                                           ['DPA1*02:01'],
                                           ['DQA1*01:08']],
            "recipient_antibodies": [{'mfi': 2100,
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
