import re

import pandas as pd

from tests.test_utilities.prepare_app import DbTests
from txmatching.database.sql_alchemy_schema import ParsingErrorModel
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody
from txmatching.utils.enums import HLA_GROUP_CODE_REGEX, HLAGroup
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.hla_system.hla_transformations import (
    HlaCodeProcessingResultDetail, _try_convert_ultra_high_res,
    get_mfi_from_multiple_hla_codes, parse_hla_raw_code,
    parse_hla_raw_code_with_details, preprocess_hla_code_in)
from txmatching.utils.hla_system.hla_transformations_store import \
    parse_hla_raw_code_and_add_parsing_error_to_db_session
from txmatching.utils.hla_system.rel_dna_ser_parsing import (
    HIGH_RES_TO_SPLIT_OR_BROAD, parse_rel_dna_ser)

codes = {
    'A1': (HLACode(None, 'A1', 'A1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A32': (HLACode(None, 'A32', 'A19'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B7': (HLACode(None, 'B7', 'B7'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B51': (HLACode(None, 'B51', 'B5'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR11': (HLACode(None, 'DR11', 'DR5'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR15': (HLACode(None, 'DR15', 'DR2'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*23': (HLACode(None, 'A23', 'A9'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*23:01': (HLACode('A*23:01', 'A23', 'A9'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*23:04': (HLACode('A*23:04', 'A23', 'A9'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*24:02': (HLACode('A*24:02', 'A24', 'A9'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*01:52:01N': (HLACode('A*01:52:01N', None, None), HlaCodeProcessingResultDetail.HIGH_RES_WITH_LETTER),
    'A*02:03': (HLACode('A*02:03', 'A203', 'A203'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*11:01:35': (HLACode('A*11:01', 'A11', 'A11'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C*01:02': (HLACode('C*01:02', 'CW1', 'CW1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DPA1*01:07': (HLACode('DPA1*01:07', 'DPA1', 'DPA1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DRB4*01:01': (HLACode('DRB4*01:01', 'DR53', 'DR53'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DQB1*02:01:01:01': (HLACode('DQB1*02:01', 'DQ2', 'DQ2'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'NONEXISTENTN': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'NONEXISTENT': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'NONEXISTENT*11': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'A*68:06': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES),
    'B*46:10': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES),
    'A*02:719': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES),
    'DQA1*01:03': (HLACode('DQA1*01:03', 'DQA1', 'DQA1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DQB01': (HLACode(None, None, 'DQ1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C12': (HLACode(None, 'CW12', 'CW12'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B*15:10': (HLACode('B*15:10', 'B71', 'B70'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B*15:11': (HLACode('B*15:11', 'B75', 'B15'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C1': (HLACode(None, 'CW1', 'CW1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DPB13': (HLACode(None, 'DP13', 'DP13'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A9': (HLACode(None, None, 'A9'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A23': (HLACode(None, 'A23', 'A9'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*24:19': (HLACode('A*24:19', None, 'A9'), HlaCodeProcessingResultDetail.HIGH_RES_WITHOUT_SPLIT),
    'A*01:01:01:01': (HLACode('A*01:01', 'A1', 'A1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*01:01:01': (HLACode('A*01:01', 'A1', 'A1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*01:01': (HLACode('A*01:01', 'A1', 'A1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*01': (HLACode(None, 'A1', 'A1'), HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A99': (HLACode(None, 'A99', 'A99'), HlaCodeProcessingResultDetail.UNEXPECTED_SPLIT_RES_CODE),
    # low res regexp but not in transformation table
    'A*99': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    # ultra high res regexp but not in tranformation table
    'A*68:06:01': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'A*02:284N': (HLACode('A*02:284N', None, None), HlaCodeProcessingResultDetail.HIGH_RES_WITH_LETTER),
    'DRB1*04:280N': (HLACode('DRB1*04:280N', None, None), HlaCodeProcessingResultDetail.HIGH_RES_WITH_LETTER),
    'A*11:21N': (HLACode('A*11:21N', None, None), HlaCodeProcessingResultDetail.HIGH_RES_WITH_LETTER),
    'A*11:11:11:11N': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)
}


class TestCodeParser(DbTests):
    def test_parsing(self):
        for code, (expected_result, expected_result_detail) in codes.items():
            result = parse_hla_raw_code_with_details(code)
            self.assertTupleEqual((expected_result_detail, expected_result),
                                  (result.result_detail, result.maybe_hla_code),
                                  f'{code} was processed to {result.maybe_hla_code} '
                                  f'with result {result.result_detail} expected was: '
                                  f'{expected_result} with result {expected_result_detail}')

    def test_parsing_with_db_storing(self):
        for code, _ in codes.items():
            parse_hla_raw_code_and_add_parsing_error_to_db_session(code)
        errors = ParsingErrorModel.query.all()
        self.assertEqual(15, len(errors))

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
        self.assertSetEqual({HLACode('DPA1*01:03', 'DPA1', 'DPA1'), HLACode('DPB1*02:01', 'DP2', 'DP2')},
                            set(parse_hla_raw_code(code) for code in preprocess_hla_code_in('DP[01:03,02:01]')))

    def test_group_assignment(self):
        self.assertFalse(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.B], 'BWA1'))
        self.assertTrue(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.B], 'B1'))
        self.assertTrue(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.B], 'B111'))
        self.assertFalse(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.B], 'B'))
        self.assertFalse(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.B], 'BW4'))
        self.assertFalse(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.B], 'BW6'))

        self.assertFalse(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.A], 'BWA1'))
        self.assertTrue(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.A], 'A1'))
        self.assertTrue(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.A], 'A111'))
        self.assertFalse(re.match(HLA_GROUP_CODE_REGEX[HLAGroup.A], 'B'))

    def test_mfi_extraction(self):
        # When one value extremely low, calculate average only from such value.
        self.assertEqual(1, get_mfi_from_multiple_hla_codes([1, 3000, 4000], 2000, 'test'))
        self.assertEqual(1000, get_mfi_from_multiple_hla_codes([1000, 20000, 18000], 2000, 'test'))
        self.assertEqual(10000, get_mfi_from_multiple_hla_codes([30001, 10000], 2000, 'test'))

        # When multiple values low, calculate the average only from those values.
        self.assertEqual(900, get_mfi_from_multiple_hla_codes([1000, 900, 800, 19000, 20000, 18000], 2000, 'test'))

        # When similarly high MFIs calculate the average
        self.assertEqual(19000, get_mfi_from_multiple_hla_codes([20000, 18000], 2000, 'test'))
        self.assertEqual(5125, get_mfi_from_multiple_hla_codes([4000, 5000, 5500, 6000], 2000, 'test'))
        self.assertEqual(15000, get_mfi_from_multiple_hla_codes([20000, 10000], 2000, 'test'))

        # When the lowest MFI is significantly lower than the other values, but there are not MFIs close to such lowest
        # value, average of values lower then overall average is calculated. This might not be optimal in some cases,
        # as the one below (one might maybe drop the hla code. But the algorithm is better safe than sorry.)
        # This case is reported in logger and will be investigated on per instance basis.
        self.assertEqual(2500, get_mfi_from_multiple_hla_codes([4000, 5000, 5500, 6000, 1000], 2000, 'test'))

        # Checks that we truly group by high res codes. In this case both DQA1*01:01 and DQA1*01:02 are DQA1 in split.
        # DQA1*01:01 is dropped whereas DQA1*01:02 is kept.
        self.assertSetEqual({HLACode('DQA1*01:02', 'DQA1', 'DQA1')}, {hla_antibody.code for hla_antibody in HLAAntibodies(
            [
                HLAAntibody('DQA1*01:02', cutoff=2000, mfi=2500),
                HLAAntibody('DQA1*01:01', cutoff=2000, mfi=10)
            ]
        ).hla_antibodies_per_groups_over_cutoff[3].hla_antibody_list})
        # Similar case as in the lines above. All hla_codes are the same in high res. This invokes call of
        # get_mfi_from_multiple_hla_codes, where the average is calculated (1900), which is below cutoff.
        # The antibody is not removed.
        self.assertSetEqual({HLACode('DQA1*01:02', 'DQA1', 'DQA1')}, {hla_antibody.code for hla_antibody in HLAAntibodies(
                [
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=6000),
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=2000),
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=1800)
                ]
            ).hla_antibodies_per_groups[3].hla_antibody_list})

        self.assertSetEqual({
            HLAAntibody(raw_code='DQA1*01:01', mfi=4500, cutoff=2000),
            HLAAntibody(raw_code='DQA1*01:02', mfi=2000, cutoff=2000)
        }, set(
            HLAAntibodies(
                [
                    HLAAntibody('DQA1*01:01', cutoff=2000, mfi=6000),
                    HLAAntibody('DQA1*01:02', cutoff=2000, mfi=2000),
                    HLAAntibody('DQA1*01:01', cutoff=2000, mfi=3000)
                ]
            ).hla_antibodies_per_groups[3].hla_antibody_list))

    def test_no_ultra_high_res_with_multiple_splits(self):
        """
        Test that for each high res code in HIGH_RES_TO_SPLIT_OR_BROAD has the same split code as all corresponding
        ultra high res codes.
        """
        high_res_to_splits = dict()
        for high_res_or_ultra_high_res, split_or_broad in HIGH_RES_TO_SPLIT_OR_BROAD.items():
            if split_or_broad is None:
                continue
            maybe_high_res = _try_convert_ultra_high_res(high_res_or_ultra_high_res)
            if maybe_high_res is not None:
                if maybe_high_res not in high_res_to_splits:
                    high_res_to_splits[maybe_high_res] = set()
                high_res_to_splits[maybe_high_res].add(split_or_broad)

        split_counts = {len(split_to_high_res) for split_to_high_res in high_res_to_splits.values()}

        self.assertSetEqual({1}, split_counts)
