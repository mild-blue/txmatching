import unittest

from txmatching.utils.hla_system.hla_transformations import (
    HlaCodeProcessingResultDetail, any_code_to_split, parse_code)

codes = {
    'A1': ('A1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A32': ('A32', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B7': ('B7', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B51': ('B51', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR11': ('DR11', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR15': ('DR15', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*02:03': ('A203', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*11:01:35': ('A11', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C*01:02': ('Cw1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DPA1*01:07': (None, HlaCodeProcessingResultDetail.UNEXPECTED_HIGH_RES_CODE),
    'DRB4*01:01': ('DRB453', HlaCodeProcessingResultDetail.UNEXPECTED_SPLIT_RES_CODE),
    'DQB1*02:01:01:01': ('DQB12', HlaCodeProcessingResultDetail.UNEXPECTED_SPLIT_RES_CODE),

}


class TestCodeParser(unittest.TestCase):
    def test_parsing(self):
        for code, (expected_result, expected_result_detail) in codes.items():
            result = any_code_to_split(code)
            parse_code(code)
            self.assertEqual(expected_result, result.maybe_hla_code,
                             f'{code} was processed to {result.maybe_hla_code}'
                             f' not correctly')
            self.assertEqual(expected_result_detail, result.result_detail,
                             f'{code} was processed to {result.result_detail}'
                             f' not correctly')
