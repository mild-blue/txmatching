from cmath import nan
import pandas as pd
import unittest

from txmatching.optimizer.compatibility_info import CompatibilityInfo
from txmatching.optimizer.optimizer_functions import parse_csv_to_comp_info, parse_csv_to_pairs, parse_json_to_config

class TestOptimizerFunctions(unittest.TestCase):
    def test_parse_csv_to_comp_info(self):
        column_names = ['donor_id', 'recipient_id', 'age_diff', 'donor_age_diff', 'other_parameter']
        data = [[1, 4, 1, 0, 15], [2, 7, 1, 1, 12], [2, 8, 4, 2, 1], [8, 7, 2, 7, 12]]

        df = pd.DataFrame(data, columns=column_names)
        csv_file = df.to_csv()

        output = parse_csv_to_comp_info(csv_file)

        expected_scoring_column_to_index = {"age_diff": 0, "donor_age_diff": 1, "other_parameter": 2}
        expected_compatibility_info = {(1, 4): [1, 0, 15], (2, 7): [1, 1, 12], (2, 8): [4, 2, 1], (8, 7): [2, 7, 12]}

        self.assertEqual(expected_scoring_column_to_index, output.scoring_column_to_index)
        self.assertEqual(expected_compatibility_info, output.compatibility_info)

        data = [[1, 4, 1, -1, 15], [2, 7, 1, 1, 12], [2, 8, 4, 2, 1], [8, 7, 2, 7, 12]]
        df = pd.DataFrame(data, columns=column_names)
        csv_file = df.to_csv()

        with self.assertRaises(ValueError):
            parse_csv_to_comp_info(csv_file)

    def test_parse_csv_to_pairs(self):
        column_names = ['donor_id', 'recipient_id']
        data = [[1, 4], [7, 1], [2, 8], [4, nan], [4, 2], [8, 7], [3, 1]]

        df = pd.DataFrame(data, columns=column_names)
        csv_file = df.to_csv()

        comp_info = CompatibilityInfo(scoring_column_to_index=None, compatibility_info=None)
        output = parse_csv_to_pairs(csv_file, comp_info)

        expected_d_to_r_pairs = {1: 4, 7: 1, 2: 8, 4: 2, 8: 7, 3: 1}
        expected_non_directed_donors = [4]

        self.assertEqual(expected_d_to_r_pairs, output.d_to_r_pairs)
        self.assertEqual(expected_non_directed_donors, output.non_directed_donors)

        data = [[1, 4], [7, 1], [2, 8], [4, nan], [4, 2], [7, 7], [3, 1]]

        df = pd.DataFrame(data, columns=column_names)
        csv_file = df.to_csv()

        with self.assertRaises(ValueError):
            parse_csv_to_pairs(csv_file, comp_info)

        parse_csv_to_pairs(csv_file, comp_info)

    def test_parse_json_to_config(self):
        return None
