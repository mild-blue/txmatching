import unittest

from kidney_exchange.utils.hla_system.split_to_broad_resolution import hla_split_to_broad
from tests.patients.test_patient_parameters import donor_parameters_Joe, recipient_parameters_Jack


class TestHighResolutionToLowResolution(unittest.TestCase):
    def setUp(self):
        self._original_high_and_expected_low_res = [(donor_parameters_Joe.hla_antigens,
                                                     ['A11', 'A10', 'B16', 'B15', 'DR4', 'DR5', 'DR52', 'DR53', 'DQ3',
                                                      'DQ3', 'DP2', 'DP10', 'Cw3', 'Cw12']
                                                     ),
                                                    (recipient_parameters_Jack.hla_antigens,
                                                     ['A1', 'A19', 'B14', 'B15', 'B15', 'B15', 'B14', 'B14', 'B15',
                                                      'B15', 'B15', 'DR4', 'DR5']
                                                     )]

    def test_hla_high_to_low_res(self):
        print("[INFO] Testing hla_high_to_low_res")
        for high_res_codes, expected_low_res_codes in self._original_high_and_expected_low_res:
            calculated_low_res_codes = [hla_split_to_broad(code) for code in high_res_codes.codes]
            self.assertEqual(calculated_low_res_codes, expected_low_res_codes)
        print("    -- done\n")
