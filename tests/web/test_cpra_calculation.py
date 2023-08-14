from tests.test_utilities.prepare_app_for_tests import DbTests

from txmatching.web import API_VERSION, CROSSMATCH_NAMESPACE


class TestCalculateCPRA(DbTests):

    def test_calculate_cpra_api(self):
        # CASE: SPLIT only
        json_split = {
            'hla_antibodies': [
                {
                    'name': 'A1',
                    'mfi': 3000,
                    'cutoff': 2000
                },
                {
                    'name': 'A32',
                    'mfi': 2200,
                    'cutoff': 2000
                },
                {
                    'name': 'B7',
                    'mfi': 2100,
                    'cutoff': 2000
                }
            ]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/calculate-cpra', json=json_split,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(res.json['cpra'], 51.84)

        # CASE: HIGH RES only
        json_high_res = {
            'hla_antibodies': [
                {
                    'name': 'A*02:03',
                    'mfi': 2010,
                    'cutoff': 2000
                },
                {
                    'name': 'A*11:01:35',
                    'mfi': 2500,
                    'cutoff': 2000
                },
                {
                    'name': 'DRB4*01:01',
                    'mfi': 3000,
                    'cutoff': 2000
                },
                {
                    'name': 'DP[02:01,02:01]',
                    'mfi': 3000,
                    'cutoff': 2000
                },
                {
                    'name': 'DQ[02:01,02:01]',
                    'mfi': 2500,
                    'cutoff': 2000
                }
            ]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/calculate-cpra', json=json_high_res,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(res.json['cpra'], 80.48)

        # CASE: MIX (SPLIT + HIGH RES)
        json_mix = {
            'hla_antibodies': json_split['hla_antibodies'] + json_high_res['hla_antibodies']
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/calculate-cpra', json=json_mix,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(res.json['cpra'], 90.76)

        # CASE: no antibodies
        json_empty = {
            'hla_antibodies': []
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/calculate-cpra', json=json_empty,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(res.json['cpra'], 0)
