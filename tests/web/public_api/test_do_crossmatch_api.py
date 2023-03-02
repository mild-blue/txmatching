from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.web import API_VERSION, PUBLIC_NAMESPACE


class TestDoCrossmatchApi(DbTests):

    def test_do_crossmatch_api(self):
        json = {
            "donor_hla_typing": ['A*02:02', 'A*01:01'],
            "recipient_antibodies": [{'mfi': 2350,
                                      'name': 'A*02:02',
                                      'cutoff': 1000
                                      },
                                     {'mfi': 5000,
                                      'name': 'A*01:01',
                                      'cutoff': 1000
                                      }],
        }

        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{PUBLIC_NAMESPACE}/do-crossmatch', json=json,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual({'hla_antibody': {'code': {'broad': 'A1', 'high_res': 'A*01:01', 'split': 'A1'},
                                               'cutoff': 1000, 'mfi': 5000, 'raw_code': 'A*01:01'},
                              'match_type': 'HIGH_RES'},
                             res.json['crossmatched_antibodies_per_group'][0]['antibody_matches'][0])
            self.assertEqual({'hla_antibody': {'code': {'broad': 'A2', 'high_res': 'A*02:02', 'split': 'A2'},
                                               'cutoff': 1000, 'mfi': 2350, 'raw_code': 'A*02:02'},
                              'match_type': 'HIGH_RES'},
                             res.json['crossmatched_antibodies_per_group'][0]['antibody_matches'][1])
            self.assertEqual(
                'All antibodies are in high resolution, and all of them are above cutoff. This is fine and antibodies '
                'will be processed properly, but  it is better to all antibodies the patient was tested for to improve '
                'crossmatch estimation.',
                res.json['parsing_issues'][0]['message'])
            self.assertEqual('This HLA group should contain at least one antigen.',
                             res.json['parsing_issues'][1]['message'])
            self.assertEqual('This HLA group should contain at least one antigen.',
                             res.json['parsing_issues'][2]['message'])
