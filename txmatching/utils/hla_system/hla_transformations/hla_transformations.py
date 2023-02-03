import logging
import re
from typing import List

from txmatching.utils.hla_system.hla_regexes import (
    HIGH_RES_REGEX_ENDING_WITH_LETTER, HIGH_RES_WITH_SUBUNITS_REGEX,
    LOW_RES_REGEX, SPLIT_RES_REGEX, try_get_hla_high_res)
from txmatching.utils.hla_system.hla_table import (
    ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE, ALL_ULTRA_HIGH_RES_CODES,
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
def parse_hla_raw_code_with_details(hla_raw_code: str) -> HlaCodeProcessingResult:
    if hla_raw_code in PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS:
        return process_parsing_result(hla_raw_code, PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS[hla_raw_code],
                                      ParsingIssueDetail.SUCCESSFULLY_PARSED)
    if re.match(LOW_RES_REGEX, hla_raw_code):
        exception_split_broad_code = high_res_low_res_to_split_or_broad(hla_raw_code)
        if isinstance(exception_split_broad_code, ParsingIssueDetail):
            return process_parsing_result(hla_raw_code, hla_raw_code, exception_split_broad_code)
        logger.warning(f'Low res code {hla_raw_code} parsed as split code {exception_split_broad_code}')
        return process_parsing_result(None, exception_split_broad_code)

    if re.match(SPLIT_RES_REGEX, hla_raw_code):
        return process_parsing_result(None, hla_raw_code)

    maybe_high_res = try_get_hla_high_res(hla_raw_code)
    if maybe_high_res:
        if maybe_high_res != hla_raw_code:
            logger.warning(f'Ultra high resolution {hla_raw_code} parsed as high resolution {maybe_high_res}')
        return _process_hla_in_high_res(maybe_high_res, hla_raw_code)

    maybe_high_res_letter_match = try_get_hla_high_res(hla_raw_code,
                                                       regex=HIGH_RES_REGEX_ENDING_WITH_LETTER)
    if maybe_high_res_letter_match:
        if (maybe_high_res_letter_match in ALL_ULTRA_HIGH_RES_CODES
                or hla_raw_code in ALL_ULTRA_HIGH_RES_CODES
                or maybe_high_res_letter_match in HIGH_RES_TO_SPLIT_OR_BROAD):
            return process_parsing_result(hla_raw_code, None, ParsingIssueDetail.HIGH_RES_WITH_LETTER)
    return process_parsing_result(hla_raw_code, hla_raw_code, ParsingIssueDetail.UNPARSABLE_HLA_CODE)


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


def _process_hla_in_high_res(hla_high_res: str, hla_raw_code: str) -> HlaCodeProcessingResult:
    exception_split_broad_code = HIGH_RES_TO_SPLIT_OR_BROAD.get(
        hla_high_res,
        None
    )
    if exception_split_broad_code is None:
        if hla_raw_code in ALL_ULTRA_HIGH_RES_CODES:
            return process_parsing_result(hla_raw_code, hla_raw_code, ParsingIssueDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES)
        else:
            return process_parsing_result(hla_raw_code, hla_raw_code, ParsingIssueDetail.UNPARSABLE_HLA_CODE)
    if isinstance(exception_split_broad_code, ParsingIssueDetail):
        return process_parsing_result(hla_raw_code, hla_raw_code, exception_split_broad_code)
    if hla_high_res in ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE:
        return process_parsing_result(hla_high_res, exception_split_broad_code,
                                      ParsingIssueDetail.HIGH_RES_WITH_ASSUMED_SPLIT_CODE)

    return process_parsing_result(hla_high_res, exception_split_broad_code)
