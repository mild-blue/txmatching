import re

import pandas as pd

from tests.test_utilities.prepare_app import DbTests
from txmatching.database.sql_alchemy_schema import ParsingErrorModel
from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody
from txmatching.utils.enums import HLA_GROUP_SPLIT_CODE_REGEX, HLAGroup
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.hla_system.hla_transformations import (
    HlaCodeProcessingResultDetail, get_mfi_from_multiple_hla_codes,
    parse_hla_raw_code, parse_hla_raw_code_with_details,
    preprocess_hla_code_in)
from txmatching.utils.hla_system.hla_transformations_store import \
    parse_hla_raw_code_and_store_parsing_error_in_db
from txmatching.utils.hla_system.rel_dna_ser_parsing import parse_rel_dna_ser

codes = {
    'A1': ('A1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A32': ('A32', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B7': ('B7', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B51': ('B51', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR11': ('DR11', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR15': ('DR15', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*23': ('A23', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*23:01': ('A23', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*23:04': ('A23', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*24:02': ('A24', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*01:52:01N': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'A*02:03': ('A203', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*11:01:35': ('A11', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C*01:02': ('CW1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DPA1*01:07': ('DPA1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DRB4*01:01': ('DR53', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DQB1*02:01:01:01': ('DQ2', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'NONEXISTENT': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'NONEXISTENT*11': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'A*68:06': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'B*46:10': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'A*02:719': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'DQA1*01:03': ('DQA1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DQB01': ('DQ1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C12': ('CW12', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B*15:10': ('B71', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B*15:11': ('B75', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C1': ('CW1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DPB13': ('DP13', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED)
}


class TestCodeParser(DbTests):
    def test_parsing(self):
        for code, (expected_result, expected_result_detail) in codes.items():
            result = parse_hla_raw_code_with_details(code)
            parse_hla_raw_code(code)  # here just to test logging
            self.assertTupleEqual((expected_result_detail, expected_result),
                                  (result.result_detail, result.maybe_hla_code),
                                  f'{code} was processed to {result.maybe_hla_code} '
                                  f'with result {result.result_detail} expected was: '
                                  f'{expected_result} with result {expected_result_detail}')

    def test_parsing_with_db_storing(self):
        for code, _ in codes.items():
            parse_hla_raw_code_and_store_parsing_error_in_db(code)
        errors = ParsingErrorModel.query.all()
        self.assertEqual(6, len(errors))

    def test_parse_hla_ser(self):
        parsing_result = parse_rel_dna_ser(get_absolute_path('tests/utils/hla_system/rel_dna_ser_test.txt'))

        self.assertEqual('A1', parsing_result.loc['A*01:01:01:01'].split)
        self.assertTrue(pd.isna(parsing_result.loc['A*05:01:01:02N'].split))
        self.assertTrue(pd.isna(parsing_result.loc['A*06:01:01:02'].split))
        self.assertEqual('DR1', parsing_result.loc['DRB1*03:01:01:02'].split)
        self.assertEqual('DP2', parsing_result.loc['DPB1*02:01:06'].split)
        self.assertEqual('CW14', parsing_result.loc['C*14:02:01:01'].split)
        self.assertEqual('CW8', parsing_result.loc['C*09'].split)

    def test_preprocessing(self):
        self.assertSetEqual({'DPA1*01:03', 'DPB1*04:02'}, set(preprocess_hla_code_in('DP4 [01:03, 04:02]')))
        self.assertSetEqual({'DQA1*01:03', 'DQB1*06:03'}, set(preprocess_hla_code_in('DQ[01:03,      06:03]')))
        self.assertSetEqual({'DPA1', 'DP2'},
                            set(parse_hla_raw_code(code) for code in preprocess_hla_code_in('DP[01:03,02:01]')))

    def test_group_assignment(self):
        self.assertFalse(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.B], 'BWA1'))
        self.assertTrue(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.B], 'B1'))
        self.assertTrue(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.B], 'B111'))
        self.assertFalse(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.B], 'B'))
        self.assertFalse(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.B], 'BW4'))
        self.assertFalse(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.B], 'BW6'))

        self.assertFalse(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.A], 'BWA1'))
        self.assertTrue(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.A], 'A1'))
        self.assertTrue(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.A], 'A111'))
        self.assertFalse(re.match(HLA_GROUP_SPLIT_CODE_REGEX[HLAGroup.A], 'B'))

    def test_mfi_extraction(self):
        # when one value extremely low, calculate average only from such value
        self.assertEqual(1, get_mfi_from_multiple_hla_codes([1, 3000, 4000], 2000, 'test'))
        # when one value extremely low, calculate average only from such value
        self.assertEqual(1000, get_mfi_from_multiple_hla_codes([1000, 20000, 18000], 2000, 'test'))
        # When similarily high mfis calculate the average
        self.assertEqual(19000, get_mfi_from_multiple_hla_codes([20000, 18000], 2000, 'test'))
        # When similarily high mfis calculate the average
        self.assertEqual(5125, get_mfi_from_multiple_hla_codes([4000, 5000, 5500, 6000], 2000, 'test'))
        # When the lowest mfi is significantly lower than the other values, but there are not mfis close to such lowest
        # value, average of values lower then overall average is calculated. This might not be optimal in some cases,
        # as the one below (one might maybe drop the hla code. But the algorithm is better safe than sorry.
        # This cas is reported in logger and will be investigated on per instance basis.
        self.assertEqual(2500, get_mfi_from_multiple_hla_codes([4000, 5000, 5500, 6000, 1000], 2000, 'test'))
        # Average of values that differ not too much is calculated
        self.assertEqual(15000, get_mfi_from_multiple_hla_codes([20000, 10000], 2000, 'test'))
        # Only the lower value is taken for average calculatation in case the values differ too much.
        self.assertEqual(10000, get_mfi_from_multiple_hla_codes([30001, 10000], 2000, 'test'))

        # check that we truly group by high res. In this case both DQA1*01:01 and 02 are DQA1 in split. But
        # 01 is dropped whereas DQA1*01:01 is kept and after that transformed to DQA1 and therefore it is in the
        # antibody set.
        self.assertSetEqual({'DQA1'}, {hla_antibody.code for hla_antibody in HLAAntibodies(
                [
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=2500),
                    HLAAntibody('DQA1*01:01', cutoff=2000, mfi=10)
                ]
            ).hla_antibodies_per_groups[3].hla_antibody_list})
        # here is similar case as in the lines above, In all the cases the hla_code is the same and therefore this
        # should be translated to get_mfi_from_multiple_hla_codes call eventually and here average is calculated to 1900
        # which is below cutoff.
        self.assertSetEqual(set(), set(
            HLAAntibodies(
                [
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=6000),
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=2000),
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=1800)
                ]
            ).hla_antibodies_per_groups[3].hla_antibody_list))
