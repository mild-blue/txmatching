import re
from typing import List

import pandas as pd

from tests.test_utilities.hla_preparation_utils import (create_antibodies,
                                                        create_antibody,
                                                        create_hla_type)
from tests.test_utilities.prepare_app_for_tests import DbTests
from tests.utils.hla_system.type_a_example_recipient import TYPE_A_EXAMPLE_REC
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_functions import (
    HighResAntibodiesAnalysis, analyze_if_high_res_antibodies_are_type_a,
    is_all_antibodies_in_high_res)
from txmatching.patients.hla_model import HLAPerGroup
from txmatching.utils.constants import \
    SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES
from txmatching.utils.enums import HLA_GROUPS_PROPERTIES, HLAGroup
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.hla_system.hla_regexes import try_get_hla_high_res
from txmatching.utils.hla_system.hla_table import \
    PARSED_DATAFRAME_WITH_ULTRA_HIGH_RES_TRANSFORMATIONS
from txmatching.utils.hla_system.hla_transformations.get_mfi_from_multiple_hla_codes import \
    get_mfi_from_multiple_hla_codes
from txmatching.utils.hla_system.hla_transformations.hla_transformations import (
    parse_hla_raw_code_with_details, preprocess_hla_code_in)
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import (
    basic_group_is_empty, group_exceedes_max_number_of_hla_types)
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import (
    ERROR_PROCESSING_RESULTS, OK_PROCESSING_RESULTS,
    WARNING_PROCESSING_RESULTS, ParsingIssueDetail)
from txmatching.utils.hla_system.rel_dna_ser_parsing import parse_rel_dna_ser

codes = {
    'A1': (HLACode(None, 'A1', 'A1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A32': (HLACode(None, 'A32', 'A19'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'B7': (HLACode(None, 'B7', 'B7'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'B51': (HLACode(None, 'B51', 'B5'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DR11': (HLACode(None, 'DR11', 'DR5'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DR15': (HLACode(None, 'DR15', 'DR2'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*23': (HLACode(None, 'A23', 'A9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*23:01': (HLACode('A*23:01', 'A23', 'A9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*23:04': (HLACode('A*23:04', 'A23', 'A9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*24:02': (HLACode('A*24:02', 'A24', 'A9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*01:52:01N': (HLACode('A*01:52:01N', None, None), ParsingIssueDetail.HIGH_RES_WITH_LETTER),
    'A*02:03': (HLACode('A*02:03', 'A203', 'A203'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*11:01:35': (HLACode('A*11:01', 'A11', 'A11'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'C*01:02': (HLACode('C*01:02', 'CW1', 'CW1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DPA1*01:07': (HLACode('DPA1*01:07', 'DPA1', 'DPA1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DRB4*01:01': (HLACode('DRB4*01:01', 'DR53', 'DR53'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DQB1*02:01:01:01': (HLACode('DQB1*02:01', 'DQ2', 'DQ2'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DQB1*03:19:01:02Q': (HLACode('DQB1*03:19:01:02Q', None, None), ParsingIssueDetail.HIGH_RES_WITH_LETTER),
    'NONEXISTENTN': (HLACode('NONEXISTENTN', 'NONEXISTENTN', 'NONEXISTENTN'), ParsingIssueDetail.UNPARSABLE_HLA_CODE),
    'NONEXISTENT': (HLACode('NONEXISTENT', 'NONEXISTENT', 'NONEXISTENT'), ParsingIssueDetail.UNPARSABLE_HLA_CODE),
    'NONEXISTENT*11': (HLACode('NONEXISTENT*11', 'NONEXISTENT*11', 'NONEXISTENT*11'), ParsingIssueDetail.UNPARSABLE_HLA_CODE),
    'B*15:36': (HLACode('B*15:36', 'B*15:36', 'B*15:36'), ParsingIssueDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES),
    'A*68:06': (HLACode('A*68:06', 'A68', 'A28'), ParsingIssueDetail.HIGH_RES_WITH_ASSUMED_SPLIT_CODE),
    'B*46:10': (HLACode('B*46:10', 'B46', 'B46'), ParsingIssueDetail.HIGH_RES_WITH_ASSUMED_SPLIT_CODE),
    'A*02:719': (HLACode('A*02:719', 'A2', 'A2'), ParsingIssueDetail.HIGH_RES_WITH_ASSUMED_SPLIT_CODE),
    'DQA1*01:03': (HLACode('DQA1*01:03', 'DQA1', 'DQA1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DQB01': (HLACode(None, None, 'DQ1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'C12': (HLACode(None, 'CW12', 'CW12'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'B*15:10': (HLACode('B*15:10', 'B71', 'B70'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'B*15:11': (HLACode('B*15:11', 'B75', 'B15'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'C1': (HLACode(None, 'CW1', 'CW1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DPB13': (HLACode(None, 'DP13', 'DP13'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A9': (HLACode(None, None, 'A9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A23': (HLACode(None, 'A23', 'A9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*24:19': (HLACode('A*24:19', None, 'A9'), ParsingIssueDetail.HIGH_RES_WITHOUT_SPLIT),
    'A*01:01:01:01': (HLACode('A*01:01', 'A1', 'A1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*01:01:01': (HLACode('A*01:01', 'A1', 'A1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*01:01': (HLACode('A*01:01', 'A1', 'A1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*01': (HLACode(None, 'A1', 'A1'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'BW4': (HLACode(None, 'BW4', 'BW4'), ParsingIssueDetail.IRRELEVANT_CODE),
    'BW6': (HLACode(None, 'BW6', 'BW6'), ParsingIssueDetail.IRRELEVANT_CODE),
    'BW42': (HLACode(None, 'BW42', 'BW42'), ParsingIssueDetail.UNEXPECTED_SPLIT_RES_CODE),
    'A99': (HLACode(None, 'A99', 'A99'), ParsingIssueDetail.UNEXPECTED_SPLIT_RES_CODE),
    # low res regexp but not in transformation table
    'A*99': (HLACode('A*99', 'A*99', 'A*99'), ParsingIssueDetail.UNPARSABLE_HLA_CODE),
    # ultra high res regexp but not in tranformation table
    'A*02:284N': (HLACode('A*02:284N', None, None), ParsingIssueDetail.HIGH_RES_WITH_LETTER),
    'DRB1*04:280N': (HLACode('DRB1*04:280N', None, None), ParsingIssueDetail.HIGH_RES_WITH_LETTER),
    'A*11:21N': (HLACode('A*11:21N', None, None), ParsingIssueDetail.HIGH_RES_WITH_LETTER),
    'A*11:11:11:11N': (HLACode('A*11:11:11:11N', None, None), ParsingIssueDetail.HIGH_RES_WITH_LETTER),
    'DOA*01:04N': (HLACode('DOA*01:04N', 'DOA*01:04N', 'DOA*01:04N'), ParsingIssueDetail.UNPARSABLE_HLA_CODE),
    'DRB4*01:03': (HLACode('DRB4*01:03', 'DR53', 'DR53'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DRB4*01:03N': (HLACode('DRB4*01:03N', None, None), ParsingIssueDetail.HIGH_RES_WITH_LETTER),
    'B*83': (HLACode(None, 'B83', 'B83'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'B83': (HLACode(None, 'B83', 'B83'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    # See file rel_dna_ser_exceptions.py for explanation of the conversions below
    'DRB1*07:07': (HLACode('DRB1*07:07', 'DR7', 'DR7'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'B*82:02': (HLACode('B*82:02', 'B82', 'B82'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DRB1*09:02': (HLACode('DRB1*09:02', 'DR9', 'DR9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'C*07:18': (HLACode('C*07:18', 'CW7', 'CW7'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*26:12': (HLACode('A*26:12', 'A26', 'A10'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*32:03': (HLACode('A*32:03', 'A32', 'A19'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'A*24:95': (HLACode('A*24:95', 'A24', 'A9'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DRB1*10:03': (HLACode('DRB1*10:03', 'DR10', 'DR10'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
    'DQB1*03:19': (HLACode('DQB1*03:19', 'DQ7', 'DQ3'), ParsingIssueDetail.SUCCESSFULLY_PARSED),
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

    def test_checking_number_of_codes_per_group(self):
        codes_per_group = [
            HLAPerGroup(HLAGroup.A, [
                create_hla_type('A*02:68'),
                create_hla_type('A*01:25'),
                create_hla_type('A*02:67')
            ]),
            HLAPerGroup(HLAGroup.B, [
                create_hla_type('B*07:15'),
                create_hla_type('B*15:19'),
            ]),
            HLAPerGroup(HLAGroup.DRB1, [
                create_hla_type('DRB1*12:05'),
                create_hla_type('DRB1*13:16'),
                create_hla_type('DRB1*13:16'),
            ])
        ]

        expected = {'A', 'DRB1'}
        raw_codes_with_wrong_number_per_group = {group.hla_group.name for group in codes_per_group if
                                                 group_exceedes_max_number_of_hla_types(group.hla_types, group.hla_group)}

        self.assertEqual(expected, raw_codes_with_wrong_number_per_group)

    def test_number_of_codes_per_group_is_correct(self):
        codes_per_group = [
            HLAPerGroup(HLAGroup.A, []),
            HLAPerGroup(HLAGroup.B, []),
            HLAPerGroup(HLAGroup.DPA, [
                create_hla_type('DPA1*01:03'),
                create_hla_type('DPA1*01:07')
            ]),
            HLAPerGroup(HLAGroup.DPB, [
                create_hla_type('DPB1*04:01'),
                create_hla_type('DPB1*09:01')

            ])
        ]

        expected = {'A', 'B'}
        raw_codes_with_wrong_number_per_group = {group.hla_group.name for group in codes_per_group if
                                                 basic_group_is_empty(group.hla_types)}

        self.assertEqual(expected, raw_codes_with_wrong_number_per_group)

    def test_parse_hla_ser(self):
        parsing_result = parse_rel_dna_ser(get_absolute_path('tests/utils/hla_system/rel_dna_ser_test.txt'))

        self.assertEqual('A1', parsing_result.loc['A*01:01:01:01'].split)
        self.assertTrue(pd.isna(parsing_result.loc['A*05:01:01:02N'].split))
        self.assertTrue(pd.isna(parsing_result.loc['A*06:01:01:02'].split))
        self.assertTrue(pd.isna(parsing_result.loc['DPB1*936:01Q'].split))
        self.assertEqual('DR1', parsing_result.loc['DRB1*03:01:01:02'].split)
        self.assertEqual('DP2', parsing_result.loc['DPB1*02:01:06'].split)
        self.assertEqual('CW14', parsing_result.loc['C*14:02:01:01'].split)
        self.assertEqual('CW8', parsing_result.loc['C*09'].split)
        self.assertEqual('CW3', parsing_result.loc['C*03:448Q'].split)

    def test_preprocessing(self):
        self.assertSetEqual({'DPA1*01:03', 'DPB1*04:02'}, set(preprocess_hla_code_in('DP4 [01:03, 04:02]')))
        self.assertSetEqual({'DQA1*01:03', 'DQB1*06:03'}, set(preprocess_hla_code_in('DQ[01:03,      06:03]')))
        self.assertSetEqual({HLACode('DPA1*01:03', 'DPA1', 'DPA1'), HLACode('DPB1*02:01', 'DP2', 'DP2')},
                            set(create_hla_type(code).code for code in preprocess_hla_code_in('DP[01:03,02:01]')))

    def test_group_assignment(self):
        self.assertFalse(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.B].split_code_regex, 'BWA1'))
        self.assertTrue(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.B].split_code_regex, 'B1'))
        self.assertTrue(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.B].split_code_regex, 'B111'))
        self.assertFalse(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.B].split_code_regex, 'B'))
        self.assertFalse(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.B].split_code_regex, 'BW4'))
        self.assertFalse(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.B].split_code_regex, 'BW6'))

        self.assertFalse(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.A].split_code_regex, 'BWA1'))
        self.assertTrue(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.A].split_code_regex, 'A1'))
        self.assertTrue(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.A].split_code_regex, 'A111'))
        self.assertFalse(re.match(HLA_GROUPS_PROPERTIES[HLAGroup.A].split_code_regex, 'B'))

    def test_mfi_extraction(self):
        # When one value extremely low, calculate average only from such value.
        self._compare_mfi_result(expected_mfi=1, mfis=[1, 3000, 4000])
        self._compare_mfi_result(expected_mfi=1000, mfis=[1000, 20000, 18000])
        self.assertEqual(10000, get_mfi_from_multiple_hla_codes([30001, 10000], 2000, 'test')[1])

        # When multiple values low, calculate the average only from those values.
        self._compare_mfi_result(expected_mfi=900, mfis=[1000, 900, 800, 19000, 20000, 18000], has_issue=False)

        # When similarly high MFIs calculate the average
        self._compare_mfi_result(expected_mfi=19000, mfis=[20000, 18000], has_issue=False)
        self._compare_mfi_result(expected_mfi=5125, mfis=[4000, 5000, 5500, 6000], has_issue=False)
        self._compare_mfi_result(expected_mfi=10000, mfis=[20000, 10000], has_issue=False)

        # When the lowest MFI is significantly lower than the other values, but there are not MFIs close to such lowest
        # value, average of values lower then overall average is calculated. This might not be optimal in some cases,
        # as the one below (one might maybe drop the hla code. But the algorithm is better safe than sorry.)
        # This case is reported in logger and will be investigated on per instance basis.
        self._compare_mfi_result(expected_mfi=2500, mfis=[4000, 5000, 5500, 6000, 1000])

        # Checks that we truly group by high res codes. In this case both DQA1*01:01 and DQA1*01:02 are DQA1 in split.
        # DQA1*01:01 is dropped whereas DQA1*01:02 is kept.
        self.assertSetEqual({HLACode('DQA1*01:02', 'DQA1', 'DQA1')},
                            {hla_antibody.code for hla_antibody in create_antibodies(
                                [
                                    create_antibody('DQA1*01:02', cutoff=2000, mfi=2500),
                                    create_antibody('DQA1*01:01', cutoff=2000, mfi=10)
                                ]
                            ).hla_antibodies_per_groups_over_cutoff[6].hla_antibody_list})
        # Similar case as in the lines above. All hla_codes are the same in high res. This invokes call of
        # get_mfi_from_multiple_hla_codes, where the average is calculated (1900), which is below cutoff.
        # The antibody is not removed.
        self.assertSetEqual({HLACode('DQA1*01:02', 'DQA1', 'DQA1')},
                            {hla_antibody.code for hla_antibody in create_antibodies(
                                [
                                    create_antibody('DQA1*01:02', cutoff=2000, mfi=6000),
                                    create_antibody('DQA1*01:02', cutoff=2000, mfi=2000),
                                    create_antibody('DQA1*01:02', cutoff=2000, mfi=1800)
                                ]
                            ).hla_antibodies_per_groups[6].hla_antibody_list})

        self.assertSetEqual({
            create_antibody(raw_code='DQA1*01:01', mfi=3000, cutoff=2000),
            create_antibody(raw_code='DQA1*01:02', mfi=2000, cutoff=2000)
        }, set(
            create_antibodies(
                [
                    create_antibody('DQA1*01:01', cutoff=2000, mfi=6000),
                    create_antibody('DQA1*01:02', cutoff=2000, mfi=2000),
                    create_antibody('DQA1*01:01', cutoff=2000, mfi=3000)
                ]
            ).hla_antibodies_per_groups[6].hla_antibody_list))
        # When MFI quite close to each other but one below and one above cutoff
        self._compare_mfi_result(expected_mfi=1500, mfis=[1500, 2900])
        # no warning in case the values are all quite low:
        self._compare_mfi_result(expected_mfi=1201, mfis=[1339, 1058, 2058, 1206], has_issue=False)
        self._compare_mfi_result(expected_mfi=1508, mfis=[3970, 1922, 1422, 1180], has_issue=True)

    def test_no_ultra_high_res_with_multiple_splits(self):
        """
        Test that for each high res code in HIGH_RES_TO_SPLIT_OR_BROAD has the same split code as all corresponding
        ultra high res codes.
        """
        high_res_to_splits = {}
        all_codes = PARSED_DATAFRAME_WITH_ULTRA_HIGH_RES_TRANSFORMATIONS.split.to_dict()
        for high_res_or_ultra_high_res, split_or_broad in all_codes.items():
            if split_or_broad is None:
                continue
            maybe_high_res = try_get_hla_high_res(high_res_or_ultra_high_res)
            if maybe_high_res is not None:
                if maybe_high_res not in high_res_to_splits:
                    high_res_to_splits[maybe_high_res] = set()
                high_res_to_splits[maybe_high_res].add(split_or_broad)

        split_counts = {len(split_to_high_res) for split_to_high_res in high_res_to_splits.values()}

        self.assertSetEqual({1}, split_counts)

    def test_parsing_issues_exactly_in_one_severity_category(self):

        for processing_result in ParsingIssueDetail:
            self.assertTrue(
                (processing_result in OK_PROCESSING_RESULTS or
                 processing_result in WARNING_PROCESSING_RESULTS or
                 processing_result in ERROR_PROCESSING_RESULTS)
            )

        for processing_result in OK_PROCESSING_RESULTS:
            self.assertTrue(
                (processing_result not in WARNING_PROCESSING_RESULTS and
                 processing_result not in ERROR_PROCESSING_RESULTS)
            )

        for processing_result in WARNING_PROCESSING_RESULTS:
            self.assertTrue(
                (processing_result not in OK_PROCESSING_RESULTS and
                 processing_result not in ERROR_PROCESSING_RESULTS)
            )

        for processing_result in ERROR_PROCESSING_RESULTS:
            self.assertTrue(
                (processing_result not in OK_PROCESSING_RESULTS and
                 processing_result not in WARNING_PROCESSING_RESULTS)
            )

    def test_is_all_antibodies_in_high_res(self):
        antibodies = create_antibodies(TYPE_A_EXAMPLE_REC)
        for antibodies_per_group in antibodies.hla_antibodies_per_groups:
            # general case
            self.assertTrue(is_all_antibodies_in_high_res(antibodies_per_group.hla_antibody_list))

            # not all in high res
            if antibodies_per_group.hla_group is not HLAGroup.INVALID_CODES:
                antibodies_per_group.hla_antibody_list[0] = create_antibody('A9', 2100, 2000)
                self.assertFalse(is_all_antibodies_in_high_res(antibodies_per_group.hla_antibody_list))

    def test_analyze_if_high_res_antibodies_are_type_a(self):
        antibodies = create_antibodies(TYPE_A_EXAMPLE_REC)

        # general case
        expected = HighResAntibodiesAnalysis(True, None)
        antibodies_list = []
        for antibodies_per_group in antibodies.hla_antibodies_per_groups:
            antibodies_list.extend(antibodies_per_group.hla_antibody_list)
        self.assertEqual(expected, analyze_if_high_res_antibodies_are_type_a(antibodies_list))

        for antibodies_per_group in antibodies.hla_antibodies_per_groups:
            # insufficient amount of antibodies
            if antibodies_per_group.hla_group is not HLAGroup.INVALID_CODES:
                antibodies_per_group.hla_antibody_list[0] = create_antibody('A*23:01', 2000, 2100)
                expected = HighResAntibodiesAnalysis(False,
                                                    ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES)
                self.assertEqual(expected,
                                analyze_if_high_res_antibodies_are_type_a(
                                    antibodies_per_group.hla_antibody_list[
                                    :SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES - 1]))

        # all antibodies are above cutoff:
        some_antibodies_list = antibodies.hla_antibodies_per_groups[0].hla_antibody_list
        for antibody in some_antibodies_list:
            antibody.cutoff = 2000
            antibody.mfi = 2100
        expected = HighResAntibodiesAnalysis(False,
                                             ParsingIssueDetail.ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES)
        self.assertEqual(expected,
                         analyze_if_high_res_antibodies_are_type_a(some_antibodies_list))

    def _compare_mfi_result(self, mfis: List[int], expected_mfi: int, cutoff=2000, has_issue: bool = True):
        res = get_mfi_from_multiple_hla_codes(mfis, cutoff, 'test')
        self.assertEqual(expected_mfi, res[1])
        self.assertEqual(has_issue, len(res[0]) > 0)
