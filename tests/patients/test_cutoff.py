import unittest

from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody


class TestCutOff(unittest.TestCase):
    def test_cutoff_works(self):
        hla_antibodies = HLAAntibodies(
            hla_antibodies_list=[HLAAntibody('A1', 10, 20), HLAAntibody('A2', 10, 5)])
        self.assertListEqual(
            [HLACode(None, 'A2', 'A2')],
            [hla.code for group_codes in hla_antibodies.hla_antibodies_per_groups_over_cutoff for hla in
             group_codes.hla_antibody_list]
        )
