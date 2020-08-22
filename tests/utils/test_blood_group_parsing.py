import unittest

import numpy as np

from txmatching.utils.excel_parsing.parse_excel_data import _parse_acceptable_blood_groups


class TestAcceptableBloodGroupParsing(unittest.TestCase):
    def test_acceptable_blood_group_parsing(self):
        self.assertEqual({"A", "0"}, set(_parse_acceptable_blood_groups(np.nan, "A")))
        self.assertEqual({"0", "A", "B"}, set(_parse_acceptable_blood_groups('0,B', "A")))
        self.assertEqual({"0", 'A'}, set(_parse_acceptable_blood_groups('0', "A")))
