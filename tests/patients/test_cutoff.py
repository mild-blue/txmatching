import unittest

from txmatching.patients.patient_parameters import HLAAntibodies, HLAAntibody


class TestCutOff(unittest.TestCase):
    def test_cutoff_works(self):
        hla_antibodies = HLAAntibodies(
            hla_antibodies_list=[HLAAntibody('A1', 10, 20, 'A1'), HLAAntibody('A2', 10, 5, 'A2')])
        self.assertListEqual(['A2'], [code for group_codes in hla_antibodies.hla_codes_over_cutoff_per_group for code in
                                      group_codes.hla_codes])
