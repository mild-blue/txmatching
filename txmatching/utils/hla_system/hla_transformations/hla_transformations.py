import logging
import re
from typing import List, Optional

from txmatching.utils.enums import StrictnessType
from txmatching.utils.hla_system.hla_regexes import (
    HIGH_RES_REGEX, HIGH_RES_REGEX_ENDING_WITH_LETTER,
    HIGH_RES_WITH_SUBUNITS_REGEX, LOW_RES_REGEX, SPLIT_RES_REGEX)
from txmatching.utils.hla_system.hla_table import (
    ALL_HIGH_RES_CODES, ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE,
    HIGH_RES_TO_SPLIT_OR_BROAD, high_res_low_res_to_split_or_broad)
from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result import \
    HlaCodeProcessingResult
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.utils.hla_system.hla_transformations.utils import \
    process_parsing_result
from txmatching.utils.hla_system.rel_dna_ser_exceptions import (
    PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS,
    PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES)

logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements
def parse_hla_raw_code_with_details(hla_raw_code: str,
                                    strictness_type: StrictnessType = StrictnessType.STRICT) -> HlaCodeProcessingResult:
    if hla_raw_code in PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS:
        return process_parsing_result(hla_raw_code, PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS[hla_raw_code],
                                      ParsingIssueDetail.HIGH_RES_WITH_ASSUMED_SPLIT_CODE,
                                      strictness_type=strictness_type)
    if re.match(LOW_RES_REGEX, hla_raw_code):
        exception_split_broad_code = high_res_low_res_to_split_or_broad(hla_raw_code)
        if isinstance(exception_split_broad_code, ParsingIssueDetail):
            return HlaCodeProcessingResult(None, exception_split_broad_code)
        logger.warning(f'Low res code {hla_raw_code} parsed as split code {exception_split_broad_code}')
        return process_parsing_result(None, exception_split_broad_code, strictness_type=strictness_type)

    if re.match(SPLIT_RES_REGEX, hla_raw_code):
        return process_parsing_result(None, hla_raw_code, strictness_type=strictness_type)

    standartized_high_res = _get_standartized_high_res(hla_raw_code)
    if standartized_high_res:
        if standartized_high_res != hla_raw_code:
            logger.warning(f'Ultra high resolution {hla_raw_code} parsed as high resolution {standartized_high_res}')
        return _process_standartized_high_res(standartized_high_res, hla_raw_code, strictness_type=strictness_type)

    standartized_high_res_letter_match = _get_standartized_high_res(hla_raw_code, HIGH_RES_REGEX_ENDING_WITH_LETTER)
    if standartized_high_res_letter_match:
        if (standartized_high_res_letter_match in ALL_HIGH_RES_CODES
                or hla_raw_code in ALL_HIGH_RES_CODES
                or standartized_high_res_letter_match in HIGH_RES_TO_SPLIT_OR_BROAD):
            return process_parsing_result(hla_raw_code, None, ParsingIssueDetail.HIGH_RES_WITH_LETTER,
                                          strictness_type=strictness_type)
        else:
            return HlaCodeProcessingResult(None, ParsingIssueDetail.UNPARSABLE_HLA_CODE)

    return HlaCodeProcessingResult(None, ParsingIssueDetail.UNPARSABLE_HLA_CODE)


def preprocess_hla_code_in(hla_code_in: str) -> List[str]:
    hla_code_in = hla_code_in.replace(' ', '')
    hla_code_in = hla_code_in.upper()
    matched_multi_hla_codes = re.match(HIGH_RES_WITH_SUBUNITS_REGEX, hla_code_in)
    if matched_multi_hla_codes:
        return [f'{matched_multi_hla_codes.group(1)}A1*{matched_multi_hla_codes.group(2)}',
                f'{matched_multi_hla_codes.group(1)}B1*{matched_multi_hla_codes.group(3)}']
    # TODO Handle this case better and elsewhere: https://github.com/mild-blue/txmatching/issues/1036
    elif PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.get(hla_code_in):
        return PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.get(hla_code_in)
    else:
        return [hla_code_in]


def _get_standartized_high_res(hla_raw_code: str, regex=HIGH_RES_REGEX) -> Optional[str]:
    high_res_match = regex.search(hla_raw_code)
    if high_res_match:
        standartized_high_res = high_res_match.group(1)
        return standartized_high_res
    return None


def _process_standartized_high_res(standartized_high_res: str, hla_raw_code: str,
                                   strictness_type: StrictnessType = StrictnessType.STRICT):
    exception_split_broad_code = HIGH_RES_TO_SPLIT_OR_BROAD.get(
        standartized_high_res,
        None
    )
    if exception_split_broad_code is None:
        if strictness_type == strictness_type.FORGIVING:
            return process_parsing_result(standartized_high_res, None, ParsingIssueDetail.FORGIVING_HLA_PARSING)
        if hla_raw_code in ALL_HIGH_RES_CODES:
            return HlaCodeProcessingResult(None, ParsingIssueDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES)
        else:
            return HlaCodeProcessingResult(None, ParsingIssueDetail.UNPARSABLE_HLA_CODE)
    if isinstance(exception_split_broad_code, ParsingIssueDetail):
        return HlaCodeProcessingResult(None, exception_split_broad_code)
    if standartized_high_res in ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE:
        if strictness_type == StrictnessType.FORGIVING:
            return process_parsing_result(standartized_high_res, exception_split_broad_code,
                                          ParsingIssueDetail.FORGIVING_HLA_PARSING)
        return process_parsing_result(standartized_high_res, exception_split_broad_code,
                                      ParsingIssueDetail.HIGH_RES_WITH_ASSUMED_SPLIT_CODE,
                                      strictness_type=strictness_type)

    return process_parsing_result(standartized_high_res, exception_split_broad_code, strictness_type=strictness_type)
