from dataclasses import asdict

from tests.test_utilities.prepare_app_for_tests import DbTests
from tests.test_utilities.type_A_antibodies import type_A_antibodies
from txmatching.patients.hla_code import HLACode
from txmatching.utils.hla_system.hla_cadaverous_crossmatch import (
    CadaverousCrossmatchDetailsIssues, CrossmatchSummary)
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE


class TestDoCrossmatchApi(DbTests):


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
                                      'name': 'DPA1*01:07',
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
