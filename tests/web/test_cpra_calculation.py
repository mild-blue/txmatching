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

    def test_with_integration_data(self):
        json = {
            'patient_id': 'DCODE',
            'sample_id': 'D_SAMPLE_ID',
            'datetime': '2020-8-9T20:00:00.474Z',
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
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/calculate-cpra',
                              json=json, headers=self.auth_headers)
            self.assertEqual(200, res.status_code)

            self.assertEqual(json['patient_id'], res.json['patient_id'])
            self.assertEqual(json['sample_id'], res.json['sample_id'])
            self.assertEqual(json['datetime'], res.json['datetime'])

    def test_calculate_theoretical_ab(self):
        data = {
            'hla_antibodies': [
                {
                    'cutoff': 2000,
                    'mfi': 275,
                    'name': 'DRB1*01:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 340,
                    'name': 'DRB1*01:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 263,
                    'name': 'DRB1*01:03'
                },
                {
                    'cutoff': 2000,
                    'mfi': 1061,
                    'name': 'DRB1*03:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 742,
                    'name': 'DRB1*03:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 813,
                    'name': 'DRB1*03:03'
                },
                {
                    'cutoff': 2000,
                    'mfi': 632,
                    'name': 'DRB1*04:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 489,
                    'name': 'DRB1*04:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 585,
                    'name': 'DRB1*04:03'
                },
                {
                    'cutoff': 2000,
                    'mfi': 596,
                    'name': 'DRB1*04:04'
                },
                {
                    'cutoff': 2000,
                    'mfi': 809,
                    'name': 'DRB1*04:05'
                },
                {
                    'cutoff': 2000,
                    'mfi': 1932,
                    'name': 'DRB1*07:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 495,
                    'name': 'DRB1*08:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 312,
                    'name': 'DRB1*08:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 1499,
                    'name': 'DRB1*09:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 237,
                    'name': 'DRB1*10:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 567,
                    'name': 'DRB1*11:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 465,
                    'name': 'DRB1*11:03'
                },
                {
                    'cutoff': 2000,
                    'mfi': 510,
                    'name': 'DRB1*11:04'
                },
                {
                    'cutoff': 2000,
                    'mfi': 1517,
                    'name': 'DRB1*12:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 2316,
                    'name': 'DRB1*12:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 444,
                    'name': 'DRB1*13:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 465,
                    'name': 'DRB1*13:03'
                },
                {
                    'cutoff': 2000,
                    'mfi': 574,
                    'name': 'DRB1*13:05'
                },
                {
                    'cutoff': 2000,
                    'mfi': 529,
                    'name': 'DRB1*14:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 302,
                    'name': 'DRB1*14:03'
                },
                {
                    'cutoff': 2000,
                    'mfi': 698,
                    'name': 'DRB1*14:04'
                },
                {
                    'cutoff': 2000,
                    'mfi': 370,
                    'name': 'DRB1*15:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 371,
                    'name': 'DRB1*15:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 328,
                    'name': 'DRB1*15:03'
                },
                {
                    'cutoff': 2000,
                    'mfi': 350,
                    'name': 'DRB1*16:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 403,
                    'name': 'DRB1*16:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 2262,
                    'name': 'DRB3*01:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 461,
                    'name': 'DRB3*02:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 1649,
                    'name': 'DRB3*03:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 453,
                    'name': 'DRB4*01:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 652,
                    'name': 'DRB5*01:01'
                },
                {
                    'cutoff': 2000,
                    'mfi': 509,
                    'name': 'DRB5*02:02'
                },
                {
                    'cutoff': 2000,
                    'mfi': 461,
                    'name': 'DQ[02:01,02:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 461,
                    'name': 'DQ[02:01,02:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 541,
                    'name': 'DQ[05:01,02:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 541,
                    'name': 'DQ[05:01,02:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 464,
                    'name': 'DQ[02:01,02:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 464,
                    'name': 'DQ[02:01,02:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 463,
                    'name': 'DQ[03:02,02:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 463,
                    'name': 'DQ[03:02,02:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 496,
                    'name': 'DQ[05:01,02:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 496,
                    'name': 'DQ[05:01,02:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 563,
                    'name': 'DQ[03:01,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 563,
                    'name': 'DQ[03:01,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 386,
                    'name': 'DQ[03:02,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 386,
                    'name': 'DQ[03:02,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 451,
                    'name': 'DQ[05:01,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 451,
                    'name': 'DQ[05:01,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 484,
                    'name': 'DQ[06:01,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 484,
                    'name': 'DQ[06:01,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 584,
                    'name': 'DQ[02:01,03:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 584,
                    'name': 'DQ[02:01,03:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 631,
                    'name': 'DQ[03:01,03:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 631,
                    'name': 'DQ[03:01,03:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 512,
                    'name': 'DQ[03:02,03:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 512,
                    'name': 'DQ[03:02,03:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 569,
                    'name': 'DQ[03:02,03:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 569,
                    'name': 'DQ[03:02,03:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 314,
                    'name': 'DQ[04:01,03:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 314,
                    'name': 'DQ[04:01,03:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 500,
                    'name': 'DQ[06:01,03:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 500,
                    'name': 'DQ[06:01,03:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 427,
                    'name': 'DQ[02:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 427,
                    'name': 'DQ[02:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 343,
                    'name': 'DQ[04:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 343,
                    'name': 'DQ[04:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 657,
                    'name': 'DQ[05:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 657,
                    'name': 'DQ[05:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 477,
                    'name': 'DQ[03:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 477,
                    'name': 'DQ[03:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 453,
                    'name': 'DQ[04:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 453,
                    'name': 'DQ[04:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 505,
                    'name': 'DQ[06:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 505,
                    'name': 'DQ[06:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 912,
                    'name': 'DQ[01:01,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 912,
                    'name': 'DQ[01:01,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 313,
                    'name': 'DQ[01:02,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 313,
                    'name': 'DQ[01:02,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 462,
                    'name': 'DQ[01:02,05:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 462,
                    'name': 'DQ[01:02,05:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 1713,
                    'name': 'DQ[01:04,05:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 1713,
                    'name': 'DQ[01:04,05:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 340,
                    'name': 'DQ[01:03,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 340,
                    'name': 'DQ[01:03,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 5651,
                    'name': 'DQ[01:04,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 5651,
                    'name': 'DQ[01:04,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 360,
                    'name': 'DQ[02:01,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 360,
                    'name': 'DQ[02:01,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 357,
                    'name': 'DQ[01:02,06:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 357,
                    'name': 'DQ[01:02,06:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 557,
                    'name': 'DQ[01:03,06:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 557,
                    'name': 'DQ[01:03,06:03]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 914,
                    'name': 'DQ[01:02,06:04]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 914,
                    'name': 'DQ[01:02,06:04]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 491,
                    'name': 'DP[01:03,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 491,
                    'name': 'DP[01:03,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 663,
                    'name': 'DP[02:01,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 663,
                    'name': 'DP[02:01,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 709,
                    'name': 'DP[02:02,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 709,
                    'name': 'DP[02:02,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 652,
                    'name': 'DP[03:01,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 652,
                    'name': 'DP[03:01,01:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 239,
                    'name': 'DP[01:03,02:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 239,
                    'name': 'DP[01:03,02:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 725,
                    'name': 'DP[01:03,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 725,
                    'name': 'DP[01:03,03:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 618,
                    'name': 'DP[01:03,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 618,
                    'name': 'DP[01:03,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 663,
                    'name': 'DP[02:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 663,
                    'name': 'DP[02:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 736,
                    'name': 'DP[02:02,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 736,
                    'name': 'DP[02:02,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 625,
                    'name': 'DP[03:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 625,
                    'name': 'DP[03:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 759,
                    'name': 'DP[04:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 759,
                    'name': 'DP[04:01,04:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 285,
                    'name': 'DP[01:03,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 285,
                    'name': 'DP[01:03,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 485,
                    'name': 'DP[03:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 485,
                    'name': 'DP[03:01,04:02]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 527,
                    'name': 'DP[02:01,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 527,
                    'name': 'DP[02:01,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 674,
                    'name': 'DP[02:02,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 674,
                    'name': 'DP[02:02,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 536,
                    'name': 'DP[03:01,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 536,
                    'name': 'DP[03:01,05:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 517,
                    'name': 'DP[01:03,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 517,
                    'name': 'DP[01:03,06:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 771,
                    'name': 'DP[02:01,09:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 771,
                    'name': 'DP[02:01,09:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 593,
                    'name': 'DP[02:01,11:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 593,
                    'name': 'DP[02:01,11:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 657,
                    'name': 'DP[02:01,13:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 657,
                    'name': 'DP[02:01,13:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 471,
                    'name': 'DP[04:01,13:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 471,
                    'name': 'DP[04:01,13:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 796,
                    'name': 'DP[02:01,14:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 796,
                    'name': 'DP[02:01,14:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 372,
                    'name': 'DP[02:01,15:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 372,
                    'name': 'DP[02:01,15:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 774,
                    'name': 'DP[02:01,17:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 774,
                    'name': 'DP[02:01,17:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 333,
                    'name': 'DP[01:03,18:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 333,
                    'name': 'DP[01:03,18:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 661,
                    'name': 'DP[02:01,19:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 661,
                    'name': 'DP[02:01,19:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 734,
                    'name': 'DP[02:02,28:01]'
                },
                {
                    'cutoff': 2000,
                    'mfi': 734,
                    'name': 'DP[02:02,28:01]'
                }
            ]
        }
        with self.app.test_client() as client:
            res = client.post(f'{API_VERSION}/{CROSSMATCH_NAMESPACE}/calculate-cpra', json=data,
                              headers=self.auth_headers)
            self.assertEqual(200, res.status_code)
            self.assertEqual(res.json['cpra'], 28.5)
            self.assertCountEqual([antibody['code_sent_to_calculator'] for antibody in res.json['unacceptable_antibodies']],['DRB1*12:02', 'DRB3*01:01'])
