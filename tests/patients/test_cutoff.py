import unittest

from txmatching.patients.patient_parameters import HLAAntibodies, HLAAntibody


class TestSolveFromDbAndItsSupportFunctionality(unittest.TestCase):
    def test_cutoff_works(self):
        hla_antibodies = HLAAntibodies(
            hla_antibodies_list=[HLAAntibody('A1', 10, 20, 'A1'), HLAAntibody('A2', 10, 5, 'A2')])
        self.assertListEqual(['A2'], hla_antibodies.hla_codes_over_cutoff)
