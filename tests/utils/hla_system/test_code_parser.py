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
    'A*23': ('A23', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*01:53N': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'A*02:03': ('A203', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*11:01:35': ('A11', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C*01:02': ('CW1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DPA1*01:07': ('DPA1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DRB4*01:01': ('DR53', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DQB1*02:01:01:01': ('DQ2', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'MICA*064N': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
}


class TestCodeParser(unittest.TestCase):
    def test_parsing(self):
        for code, (expected_result, expected_result_detail) in codes.items():
            result = any_code_to_split(code)
            parse_code(code)  # here just to test logging
            self.assertTupleEqual((expected_result_detail, expected_result),
                                  (result.result_detail, result.maybe_hla_code),
                                  f'{code} was processed to {result.maybe_hla_code} '
                                  f'with result {result.result_detail} expected was: '
                                  f'{expected_result} with result {expected_result_detail}')
