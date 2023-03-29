from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE


class TestDoCrossmatchApi(DbTests):

    def test_do_crossmatch_api(self):
        # case: donor - HIGH_RES, recipient - HIGH_RES
        json = {
            "donor_hla_typing": ['A*02:02', 'A*01:01'],
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
                'All antibodies are in high resolution, some of them below cutoff and less then 20 were provided. '
                'This is fine and antibodies will be processed properly, but we are assuming that not all antibodies '
                'the patient was tested for were sent. It is better to send all to improve crossmatch estimation.',
                res.json['parsing_issues'][0]['message'])
            self.assertEqual('This HLA group should contain at least one antigen.',
                             res.json['parsing_issues'][1]['message'])
            self.assertEqual('This HLA group should contain at least one antigen.',
                             res.json['parsing_issues'][2]['message'])

    def test_do_crossmatch_api_with_different_code_formats(self):
        # case: donor - HIGH_RES, recipient - SPLIT
        json = {
            "donor_hla_typing": ['A*02:02', 'A*01:01'],
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
                'This HLA group should contain at least one antigen.',
                res.json['parsing_issues'][0]['message'])
            self.assertEqual('This HLA group should contain at least one antigen.',
                             res.json['parsing_issues'][1]['message'])

        # case: donor - SPLIT, recipient - HIGH_RES
        json = {
            "donor_hla_typing": ['A2', 'A*01:01'],
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
                'All antibodies are in high resolution, some of them below cutoff and less then 20 were provided. '
                'This is fine and antibodies will be processed properly, but we are assuming that not all antibodies '
                'the patient was tested for were sent. It is better to send all to improve crossmatch estimation.',
                res.json['parsing_issues'][0]['message'])
            self.assertEqual('This HLA group should contain at least one antigen.',
                             res.json['parsing_issues'][1]['message'])

    def test_theoretical_and_double_antibodies_not_implemented(self):
        json = {
            "donor_hla_typing": ['DPA1*01:03', 'DPA1*02:01', 'DPA1*01:04'],
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
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(501, res.status_code)
            self.assertEqual('This functionality is not currently available for dual antibodies. '
                             'We apologize and will try to change this in future versions.',
                             res.json['message'])
