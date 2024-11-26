import unittest

from txmatching.patients.hla_code import HLACode
from txmatching.utils.hla_system.hla_preparation_utils import (
    create_antibodies, create_antibody)


class TestCutOff(unittest.TestCase):
    def test_cutoff_works(self):
        hla_antibodies = create_antibodies(
            hla_antibodies_list=[create_antibody('A1', 10, 20), create_antibody('A2', 10, 5)])
        self.assertListEqual(
            [HLACode(None, 'A2', 'A2')],
            [hla.code for group_codes in hla_antibodies.hla_antibodies_per_groups_over_cutoff for hla in
             group_codes.hla_antibody_list]
        )
