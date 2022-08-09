import pandas as pd
import unittest

from txmatching.optimizer.compatibility_info import CompatibilityInfo
from txmatching.optimizer.optimizer_config import Limitations, OptimizerConfig
from txmatching.optimizer.optimizer_functions import parse_csv_to_comp_info, parse_csv_to_pairs, parse_json_to_config


class TestOptimizerFunctions(unittest.TestCase):
    def test_parse_csv_to_comp_info(self):
        column_names = ['donor_id', 'recipient_id', 'age_diff', 'donor_age_diff', 'other_parameter']
        data = [[1, 4, 1, 0, 15], [2, 7, 1, 1, 12], [2, 8, 4, 2, 1], [8, 7, 2, 7, 12]]

        csv_df = pd.DataFrame(data, columns=column_names)
        output = parse_csv_to_comp_info(csv_df)

        expected_scoring_column_to_index = {"age_diff": 0, "donor_age_diff": 1, "other_parameter": 2}
        expected_compatibility_info = {(1, 4): [1, 0, 15], (2, 7): [1, 1, 12], (2, 8): [4, 2, 1], (8, 7): [2, 7, 12]}

        self.assertEqual(expected_scoring_column_to_index, output.scoring_column_to_index)
        self.assertEqual(expected_compatibility_info, output.compatibility_info)

        data = [[1, 4, 1, -1, 15], [2, 7, 1, 1, 12], [2, 8, 4, 2, 1], [8, 7, 2, 7, 12]]
        csv_df = pd.DataFrame(data, columns=column_names)

        with self.assertRaises(ValueError):
            parse_csv_to_comp_info(csv_df)

    def test_parse_csv_to_pairs(self):
        column_names = ['donor_id', 'recipient_id']
        data = [[1, 4], [7, 1], [2, 8], [14, pd.NA], [4, 2], [8, 7], [3, 1]]

        csv_df = pd.DataFrame(data, columns=column_names)
        comp_info = CompatibilityInfo(scoring_column_to_index={}, compatibility_info={})
        output = parse_csv_to_pairs(csv_df, comp_info)

        expected_d_to_r_pairs = {1: 4, 7: 1, 2: 8, 4: 2, 8: 7, 3: 1}
        expected_non_directed_donors = [14]

        self.assertEqual(expected_d_to_r_pairs, output.d_to_r_pairs)
        self.assertEqual(expected_non_directed_donors, output.non_directed_donors)

        data = [[1, 4], [7, 1], [2, 8], [4, pd.NA], [4, 2], [7, 7], [3, 1]]
        csv_df = pd.DataFrame(data, columns=column_names)

        with self.assertRaises(ValueError):
            parse_csv_to_pairs(csv_df, comp_info)

    def test_parse_json_to_config(self):
        json_dict = {
            "limitations": {
                "max_cycle_length": 3,
                "max_chain_length": 3,
                "custom_algorithm_settings": {
                    "max_number_of_iterations": 200,
                    "something_other": 123
                }
            },
            "scoring": [
                [
                    {
                        "transplant_count": 1
                    }
                ],
                [
                    {
                        "hla_compatibility_score": 3
                    },
                    {
                        "number of donor_age_difference": 20
                    }
                ],
                [
                    {
                        "max_num_effective_two_cycles": 1
                    }
                ]
            ]
        }

        output = parse_json_to_config(json_dict)
        expected_output = OptimizerConfig(limitations=Limitations(max_cycle_length=3,
                                                                  max_chain_length=3,
                                                                  custom_algorithm_settings={
                                                                      'max_number_of_iterations': 200,
                                                                      'something_other': 123}),
                                          scoring=[[{'transplant_count': 1}],
                                                   [{'hla_compatibility_score': 3},
                                                    {'number of donor_age_difference': 20}],
                                                   [{'max_num_effective_two_cycles': 1}]])

        self.assertEqual(expected_output, output)
