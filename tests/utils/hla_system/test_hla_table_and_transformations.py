import re
import unittest

from txmatching.utils.enums import HLA_GROUP_SPLIT_CODE_REGEX, HLAGroup
from txmatching.utils.hla_system.hla_transformations import (
    HIGH_RES_REGEX, HIGH_RES_REGEX_ENDING_WITH_N, LOW_RES_REGEX,
    ULTRA_HIGH_RES_REGEX)


class TestHlaTable(unittest.TestCase):
    def test_a_b_dr_hla_code_regex(self):
        self.assertIsNotNone(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.DRB1], 'DR1'))
        self.assertIsNotNone(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.DRB1], 'DR11'))
        self.assertIsNotNone(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.A], 'A11'))
        self.assertIsNone(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.DRB1], 'DR51'))
        self.assertIsNone(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.DRB1], 'DR52'))
        self.assertIsNone(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.DRB1], 'DR53'))
        self.assertIsNotNone(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.DRB1], 'DR5'))

    def test_high_res_code_regex(self):
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'A*11'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'B*11:01'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*11:45:32'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'KW*22'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C11'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, '12983289'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*11:45:3'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*11:45:'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*111:45:'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'DPB1*1110:01'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*11:45:32Q'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'A*68:06'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'B*46:10'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'A*02:719'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX_ENDING_WITH_N, 'C*11:45N'))
        self.assertIsNone(re.match(HIGH_RES_REGEX_ENDING_WITH_N, 'KV*23N'))
        self.assertIsNone(re.match(HIGH_RES_REGEX_ENDING_WITH_N, 'DPB1*1110:01'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX_ENDING_WITH_N, 'DPB1*1110:01N'))

    def test_low_res_code_regex(self):
        self.assertIsNotNone(re.match(LOW_RES_REGEX, 'A*11'))
        self.assertIsNotNone(re.match(LOW_RES_REGEX, 'B*02'))
        self.assertIsNotNone(re.match(LOW_RES_REGEX, 'B*02N'))
        self.assertIsNotNone(re.match(LOW_RES_REGEX, 'KV*23N'))
        self.assertIsNone(re.match(LOW_RES_REGEX, 'A*68:06'))

    def test_ultra_high_res_code_regex(self):
        self.assertIsNone(re.match(ULTRA_HIGH_RES_REGEX, 'C*11:45'))
        self.assertIsNotNone(re.match(ULTRA_HIGH_RES_REGEX, 'C*11:45:32:01'))
        self.assertIsNotNone(re.match(ULTRA_HIGH_RES_REGEX, 'C*11:45:32'))
        self.assertIsNotNone(re.match(ULTRA_HIGH_RES_REGEX, 'C*11:45:32N'))
        self.assertIsNotNone(re.match(ULTRA_HIGH_RES_REGEX, 'C*11:45:32Q'))

        match = re.search(ULTRA_HIGH_RES_REGEX, 'C*11:45:32N')
        self.assertIsNotNone(match)
        self.assertEqual('C*11:45', match.group(1))

        match = re.search(ULTRA_HIGH_RES_REGEX, 'C*11:45:01:01:01:32N')
        self.assertIsNotNone(match)
        self.assertEqual('C*11:45', match.group(1))

        match = re.search(ULTRA_HIGH_RES_REGEX, 'C*11:45')
        self.assertIsNone(match)

        match = re.search(ULTRA_HIGH_RES_REGEX, 'C*11')
        self.assertIsNone(match)
