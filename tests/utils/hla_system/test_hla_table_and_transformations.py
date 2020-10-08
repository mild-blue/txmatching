import re
import unittest

from txmatching.utils.hla_system.hla_table import A_B_DR_HLA_CODE_REGEX
from txmatching.utils.hla_system.hla_transformations import HIGH_RES_REGEX


class TestHlaTable(unittest.TestCase):
    def test_a_b_dr_hla_code_regex(self):
        self.assertIsNotNone(re.match(A_B_DR_HLA_CODE_REGEX, 'DR1'))
        self.assertIsNotNone(re.match(A_B_DR_HLA_CODE_REGEX, 'DR11'))
        self.assertIsNotNone(re.match(A_B_DR_HLA_CODE_REGEX, 'A11'))
        self.assertIsNone(re.match(A_B_DR_HLA_CODE_REGEX, 'DR51'))
        self.assertIsNone(re.match(A_B_DR_HLA_CODE_REGEX, 'DR52'))
        self.assertIsNone(re.match(A_B_DR_HLA_CODE_REGEX, 'DR53'))
        self.assertIsNotNone(re.match(A_B_DR_HLA_CODE_REGEX, 'DR5'))
        self.assertIsNotNone(re.match(A_B_DR_HLA_CODE_REGEX, 'B51'))

    def test_high_res_code_regex(self):
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'A*11'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'B*11'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'C*11:45:32'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'KW*22'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'KV*23N'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'C*11:45N'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C11'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, '12983289'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*11:45:3'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*11:45:'))
        self.assertIsNone(re.match(HIGH_RES_REGEX, 'C*111:45:'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'DPB1*1110:01'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'C*11:45:32Q'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'A*68:06'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'B*46:10'))
        self.assertIsNotNone(re.match(HIGH_RES_REGEX, 'A*02:719'))
