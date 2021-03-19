import logging
import re
from typing import List

from txmatching.utils.hla_system.hla_regexes import (
    HIGH_RES_REGEX, HIGH_RES_REGEX_ENDING_WITH_LETTER,
    HIGH_RES_WITH_SUBUNITS_REGEX, LOW_RES_REGEX, SPLIT_RES_REGEX)
from txmatching.utils.hla_system.hla_table import (
    ALL_OF_THEM, STANDARD_HIGH_RES_TO_SPLIT_OR_BROAD,
    high_res_to_split_or_broad)
from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result import \
    HlaCodeProcessingResult
from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_transformations.utils import \
    process_high_res_result
from txmatching.utils.hla_system.rel_dna_ser_exceptions import (
    PARSE_HLA_CODE_EXCEPTIONS,
    PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES)

logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
def parse_hla_raw_code_with_details(hla_raw_code: str) -> HlaCodeProcessingResult:
    if hla_raw_code in PARSE_HLA_CODE_EXCEPTIONS:
        return process_high_res_result(hla_raw_code, PARSE_HLA_CODE_EXCEPTIONS[hla_raw_code])
    if re.match(LOW_RES_REGEX, hla_raw_code):
        exception_split_broad_code = high_res_to_split_or_broad(hla_raw_code)
        if isinstance(exception_split_broad_code, HlaCodeProcessingResultDetail):
            return HlaCodeProcessingResult(None, exception_split_broad_code)
        logger.warning(f'Low res code {hla_raw_code} parsed as split code {exception_split_broad_code}')
        return process_high_res_result(None, exception_split_broad_code)

    if re.match(SPLIT_RES_REGEX, hla_raw_code):
        return process_high_res_result(None, hla_raw_code)

    high_res_match = HIGH_RES_REGEX.search(hla_raw_code)
    if high_res_match and hla_raw_code:
        standartized_high_res = high_res_match.group(1)
        if standartized_high_res != hla_raw_code:
            logger.warning(f'Ultra high resolution {hla_raw_code} parsed as high resolution {standartized_high_res}')
        exception_split_broad_code = STANDARD_HIGH_RES_TO_SPLIT_OR_BROAD.get(
            standartized_high_res,
            None
        )
        if exception_split_broad_code is None:
            if hla_raw_code in ALL_OF_THEM:
                return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES)
            else:
                return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)
        if isinstance(exception_split_broad_code, HlaCodeProcessingResultDetail):
            return HlaCodeProcessingResult(None, exception_split_broad_code)

        return process_high_res_result(standartized_high_res, exception_split_broad_code)
    if re.match(HIGH_RES_REGEX_ENDING_WITH_LETTER, hla_raw_code):
        if hla_raw_code in ALL_OF_THEM:
            return process_high_res_result(hla_raw_code, None, HlaCodeProcessingResultDetail.HIGH_RES_WITH_LETTER)
        else:
            return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)

    return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)


def preprocess_hla_code_in(hla_code_in: str) -> List[str]:
    hla_code_in = hla_code_in.replace(' ', '')
    hla_code_in = hla_code_in.upper()
    matched_multi_hla_codes = re.match(HIGH_RES_WITH_SUBUNITS_REGEX, hla_code_in)
    if matched_multi_hla_codes:
        return [f'{matched_multi_hla_codes.group(1)}A1*{matched_multi_hla_codes.group(2)}',
                f'{matched_multi_hla_codes.group(1)}B1*{matched_multi_hla_codes.group(3)}']
    # Handle this case better and elsewhere: https://trello.com/c/GG7zPLyj
    elif PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.get(hla_code_in):
        return PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.get(hla_code_in)
    else:
        return [hla_code_in]
