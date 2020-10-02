import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from txmatching.utils.hla_system.hla_table import (ALL_SPLIT_BROAD_CODES,
                                                   COMPATIBILITY_BROAD_CODES,
                                                   SPLIT_TO_BROAD)
from txmatching.utils.hla_system.rel_dna_ser_parsing import HIGH_RES_TO_SPLIT

logger = logging.getLogger(__name__)

HIGH_RES_REGEX = re.compile(r'^[A-Z]+\d?\*\d\d(\:\d\d)*[A-Z]?$')
SPLIT_RES_REGEX = re.compile(r'^[A-Z]+\d+$')
C_SPLIT_FROM_HIGH_RES_REGEX = re.compile(r'^C\d+$')


def broad_to_split(hla_code: str) -> List[str]:
    if hla_code not in ALL_SPLIT_BROAD_CODES:
        logger.warning(f'Unexpected hla_code: {hla_code}')
        return [hla_code]
    splits = [split for split, broad in SPLIT_TO_BROAD.items() if broad == hla_code]
    return splits if splits else [hla_code]


def split_to_broad(hla_code: str) -> str:
    return SPLIT_TO_BROAD.get(hla_code, hla_code)


class HlaCodeProcessingResultDetail(str, Enum):
    # still returning value
    SUCCESSFULLY_PARSED = 'Code successfully parsed without anything unexpected'
    UNEXPECTED_SPLIT_RES_CODE = 'Unknown HLA code, seems to be in split resolution'
    MULTIPLE_SPLITS_FOUND = 'Multiple splits were found, unable to choose the right one.' \
                            ' Immunologists shall be contacted'
    # returning no value
    UNKNOWN_TRANSFORMATION_TO_SPLIT = 'Unable to transform high resolution HLA code. Its transformation to split' \
                                      ' code is unknown. Immunologists shall be contacted'
    UNPARSABLE_HLA_CODE = 'Completely Unexpected HLA code'


@dataclass
class HlaCodeProcessingResult:
    maybe_hla_code: Optional[str]
    result_detail: HlaCodeProcessingResultDetail


def _high_res_to_split(hla_code: str) -> Tuple[Optional[str], Optional[HlaCodeProcessingResultDetail]]:
    split_hla_code = HIGH_RES_TO_SPLIT.get(hla_code)
    issue = None
    if not split_hla_code:
        possible_split_resolutions = {split for high_res, split in HIGH_RES_TO_SPLIT.items() if
                                      high_res.startswith(hla_code)}
        if len(possible_split_resolutions) == 0:
            return None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE
        possible_split_resolutions = possible_split_resolutions.difference({None})
        if possible_split_resolutions:
            found_splits = set(possible_split_resolutions)
            if len(found_splits) == 1:
                split_hla_code = possible_split_resolutions.pop()
            else:
                # in case the number is equal we take one randomly for the moment.
                split_hla_code = None
                logger.warning(possible_split_resolutions)
                issue = HlaCodeProcessingResultDetail.MULTIPLE_SPLITS_FOUND
    if split_hla_code:
        if re.match(C_SPLIT_FROM_HIGH_RES_REGEX, split_hla_code):
            split_hla_code = f'CW{split_hla_code[1:]}'
        return split_hla_code, issue

    return None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT


# TODO https://trello.com/c/PtK2Bg27 add support for square brackets and also preprocess incoming strings in other ways
#  (move the upper there as well)
def any_code_to_split(hla_code_raw: str) -> HlaCodeProcessingResult:
    hla_code_raw = hla_code_raw.upper()
    if re.match(HIGH_RES_REGEX, hla_code_raw):
        maybe_hla_code, maybe_result_detail = _high_res_to_split(hla_code_raw)
    else:
        maybe_hla_code, maybe_result_detail = hla_code_raw, None

    if maybe_hla_code in ALL_SPLIT_BROAD_CODES:
        return HlaCodeProcessingResult(maybe_hla_code,
                                       maybe_result_detail if maybe_result_detail
                                       else HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED)

    elif maybe_hla_code and re.match(SPLIT_RES_REGEX, maybe_hla_code):
        # Some split hla codes are missing in our table, therefore we still return hla_codes if they match expected
        # format of split codes
        return HlaCodeProcessingResult(maybe_hla_code,
                                       HlaCodeProcessingResultDetail.UNEXPECTED_SPLIT_RES_CODE)

    elif maybe_result_detail:
        return HlaCodeProcessingResult(None, maybe_result_detail)
    else:
        return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)


def parse_code(hla_code: str) -> Optional[str]:
    parsing_result = any_code_to_split(hla_code)
    if not parsing_result.maybe_hla_code:
        logger.error(f'HLA code processing of {hla_code} was not successful: {parsing_result.result_detail}')
    elif parsing_result.result_detail != HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED:
        logger.warning(f'HLA code processing of {hla_code} was successful with warning: {parsing_result.result_detail}')
    return parsing_result.maybe_hla_code


def get_compatibility_broad_codes(hla_codes: List[str]) -> List[str]:
    return [split_to_broad(hla_code) for hla_code in hla_codes if split_to_broad(hla_code) in COMPATIBILITY_BROAD_CODES]
