from dataclasses import asdict

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.patients.hla_model import HLATypeWithFrequencyRaw
from txmatching.utils.hla_system.hla_cadaverous_crossmatch import \
    CadaverousCrossmatchDetailsIssues
from txmatching.utils.hla_system.hla_preparation_utils import \
    create_hla_type_with_frequency
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE


class TestDoCrossmatchApi(DbTests):


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
