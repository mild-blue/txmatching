import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set, Union

import numpy as np

from txmatching.utils.hla_system.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_table import (ALL_SPLIT_BROAD_CODES,
                                                   SPLIT_TO_BROAD)
from txmatching.utils.hla_system.rel_dna_ser_exceptions import (
    PARSE_HLA_CODE_EXCEPTIONS,
    PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES)
from txmatching.utils.hla_system.rel_dna_ser_parsing import HIGH_RES_TO_SPLIT

logger = logging.getLogger(__name__)

RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI = 1

RELATIVE_CLOSENESS_TO_CUTOFF_FROM_BELOW = 0.5
RELATIVE_CLOSENESS_TO_CUTOFF_FROM_ABOVE = 1.25
RELATIVE_CLOSENESS_TO_MINUM = 1 / 2

HIGH_RES_REGEX = re.compile(r'^[A-Z]+\d?\*\d{2,4}(:\d{2,3})*[A-Z]?$')
HIGH_RES_REGEX_ENDING_WITH_N = re.compile(r'^[A-Z]+\d?\*\d{2,4}(:\d{2,3})*N$')
SPLIT_RES_REGEX = re.compile(r'^[A-Z]+\d+$')
HIGH_RES_WITH_SUBUNITS_REGEX = re.compile(r'([A-Za-z]{1,3})\d?\[(\d{2}:\d{2}),(\d{2}:\d{2})]')

CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX = re.compile(r'C(\d+)')
B_SEROLOGICAL_CODE_WITH_W_REGEX = re.compile(r'BW(\d+)')
DQ_DP_SEROLOGICAL_CODE_WITH_AB_REGEX = re.compile(r'(D[QP])([AB])(\d+)')


def broad_to_split(hla_code: str) -> List[str]:
    if hla_code not in ALL_SPLIT_BROAD_CODES:
        logger.warning(f'Unexpected hla_code: {hla_code}')
        return [hla_code]
    splits = [split for split, broad in SPLIT_TO_BROAD.items() if broad == hla_code]
    return splits if splits else [hla_code]


def split_to_broad(hla_code: str) -> str:
    return SPLIT_TO_BROAD.get(hla_code, hla_code)


@dataclass
class HlaCodeProcessingResult:
    maybe_hla_code: Optional[str]
    result_detail: HlaCodeProcessingResultDetail


def _get_possible_splits_for_high_res_code(high_res_code: str) -> Set[str]:
    return {split for high_res, split in HIGH_RES_TO_SPLIT.items() if
            high_res.startswith(f'{high_res_code}:')}


def _high_res_to_split(high_res_code: str) -> Union[str, HlaCodeProcessingResultDetail]:
    """
    Transforms high resolution code to serological (split) code. In the case no code is found
    HlaCodeProcessingResultDetail with details is returned.
    :param high_res_code: High res code to transform.
    :return: Either found split code or HlaCodeProcessingResultDetail in case no split code is found.
    """
    maybe_split_hla_code = HIGH_RES_TO_SPLIT.get(high_res_code, _get_possible_splits_for_high_res_code(high_res_code))
    if maybe_split_hla_code is None:
        # Code found in the HIGH_RES_TO_SPLIT but none was returned as the transformation is unknown.
        return HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT
    elif isinstance(maybe_split_hla_code, str):
        return maybe_split_hla_code
    else:
        assert isinstance(maybe_split_hla_code, set), 'Unexpected type'
        if len(maybe_split_hla_code) == 0:
            # No code found in HIGH_RES_TO_SPLIT so it is code in high_res_code that does not exist in our
            # transformation table at all.
            return HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE
        possible_split_resolutions = maybe_split_hla_code.difference({None})
        if len(possible_split_resolutions) == 0:
            return HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT
        else:
            found_splits = set(possible_split_resolutions)
            if len(found_splits) == 1:
                return possible_split_resolutions.pop()
            else:
                # in case there are multiple possibilities we do not know which to choose and return None.
                logger.warning(f'Multiple possible split resolutions for high res code {high_res_code}'
                               f' found: {possible_split_resolutions}')
                return HlaCodeProcessingResultDetail.MULTIPLE_SPLITS_FOUND


def parse_hla_raw_code_with_details(hla_raw_code: str) -> HlaCodeProcessingResult:
    maybe_exception_hla_code = PARSE_HLA_CODE_EXCEPTIONS.get(hla_raw_code)
    if maybe_exception_hla_code:
        return HlaCodeProcessingResult(maybe_exception_hla_code, HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED)

    if re.match(HIGH_RES_REGEX, hla_raw_code):
        hla_code_or_error = _high_res_to_split(hla_raw_code)
    else:
        hla_code_or_error = hla_raw_code

    if isinstance(hla_code_or_error, str) and re.match(SPLIT_RES_REGEX, hla_code_or_error):
        c_match = re.match(CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX, hla_code_or_error)
        if c_match:
            hla_code_or_error = f'CW{int(c_match.group(1))}'

        b_match = re.match(B_SEROLOGICAL_CODE_WITH_W_REGEX, hla_code_or_error)
        if b_match:
            # doesn't actually do anything atm, but Bw is a special kind of antigen so we want to keep the branch here
            hla_code_or_error = f'BW{int(b_match.group(1))}'

        dpqb_match = re.match(DQ_DP_SEROLOGICAL_CODE_WITH_AB_REGEX, hla_code_or_error)
        if dpqb_match:
            subtype_str = 'A' if dpqb_match.group(2) == 'A' else ''
            hla_code_or_error = f'{dpqb_match.group(1)}{subtype_str}{int(dpqb_match.group(3))}'

        if hla_code_or_error in ALL_SPLIT_BROAD_CODES:
            return HlaCodeProcessingResult(hla_code_or_error, HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED)
        # Some split HLA codes are missing in our table, therefore we still return the found HLA code if it matches
        # expected format of split codes.
        return HlaCodeProcessingResult(hla_code_or_error,
                                       HlaCodeProcessingResultDetail.UNEXPECTED_SPLIT_RES_CODE)
    elif isinstance(hla_code_or_error, HlaCodeProcessingResultDetail):
        return HlaCodeProcessingResult(None, hla_code_or_error)
    else:
        return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)


def parse_hla_raw_code(hla_raw_code: str) -> Optional[str]:
    """
    This method is partially redundant to parse_hla_raw_code_and_store_parsing_error_in_db so in case of update,
    update it too.
    :param hla_raw_code:
    :return:
    """
    parsing_result = parse_hla_raw_code_with_details(hla_raw_code)
    if not parsing_result.maybe_hla_code:
        logger.error(f'HLA code processing of {hla_raw_code} was not successful: {parsing_result.result_detail}')
    elif parsing_result.result_detail != HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED:
        logger.warning(
            f'HLA code processing of {hla_raw_code} was successful to {parsing_result.maybe_hla_code} with warning: '
            f'{parsing_result.result_detail}')
    return parsing_result.maybe_hla_code


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
    elif re.match(HIGH_RES_REGEX_ENDING_WITH_N, hla_code_in):
        # Ignore high res codes ending with N as the allels are invalid
        return []
    else:
        return [hla_code_in]


def preprocess_hla_codes_in(hla_codes_in: List[str]) -> List[str]:
    return [parsed_code for hla_code_in in hla_codes_in for parsed_code in preprocess_hla_code_in(hla_code_in)]


def get_broad_codes(hla_codes: List[str]) -> List[str]:
    return [split_to_broad(hla_code) for hla_code in hla_codes]


def get_mfi_from_multiple_hla_codes(mfis: List[int],
                                    cutoff: int,
                                    raw_code: str,
                                    logger_with_extra_info: Union[
                                        logging.Logger, logging.LoggerAdapter] = logging.getLogger(__name__)) -> int:
    """
    Takes list of mfis of the same hla code and estimates the mfi for the code.
    It is based on discussions with immunologists. If variance is low, take average, if variance is high, take average
    only of the lower portion of mfis. If the calculated average is close to cutoff raise warning, each of such cases is
    to be checked by immunologist.

    The reason some antibodies occur multiple times is because antibodies existence is tested together for alpha and
    beta alleles. And we need to distinguish whether the MFI value relates to alpha or beta or both.

    To identify large variance to conditions have to be fulfilled:
     - difference between min max values has to be higher than cutoff.
     - relative difference between min max values has to be higher than RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI

    In such case we identify the set of the lowest MFI values and estimate the real MFI value for given hla_code only
    from them.
    """
    mfis = np.array(mfis)
    max_mfi = np.max(mfis)
    min_mfi = np.min(mfis)

    if min_mfi < 0:
        raise AssertionError(f'MFI has to be always >=0. The data shall be validated on input. Obtained MFI={min_mfi}.')

    max_min_difference = (max_mfi - min_mfi) / min_mfi if min_mfi > 0 else max_mfi
    difference_over_cutoff = (max_mfi - min_mfi) > cutoff

    only_one_number_used = False
    if max_min_difference > RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI and difference_over_cutoff:
        mfis_under_mean = mfis[mfis < np.mean(mfis)]
        mfis_close_to_minimum = mfis[mfis < min_mfi + cutoff * RELATIVE_CLOSENESS_TO_MINUM]
        # expected case: the low MFIs are identified both as close to minimum and below average. And it is not just one
        # value. Should happend in case there are two prominent groups of MFIs with large gap.
        if np.array_equal(mfis_under_mean, mfis_close_to_minimum):
            relevant_mean = np.mean(mfis_under_mean)
            # Only one value is present in the low batch. This decreases credibility of the result,
            # the value is used anyway (as instructed by immunologist) but this info is added to the warning message.
            if len(mfis_under_mean) == 1:
                only_one_number_used = True

        # Probably three (or more) different batches of MFIs. In such case only the lowest batch is used.
        elif len(min(mfis_under_mean, mfis_close_to_minimum, key=len)) > 1:
            relevant_mean = np.mean(min(mfis_under_mean, mfis_close_to_minimum, key=len))
        # Smallest batch contains only 1 MFI. Taking the large one to make the result more reliable.
        else:
            relevant_mean = np.mean(max(mfis_under_mean, mfis_close_to_minimum, key=len))

        if RELATIVE_CLOSENESS_TO_CUTOFF_FROM_BELOW * cutoff < relevant_mean < cutoff:
            logger_with_extra_info.warning(
                f'Dropping {raw_code} antibody: '
                f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                f'To be consulted with immunologist, because the antibody is dropped even though it has some high MFI '
                f'values.'
            )

        elif relevant_mean > cutoff > min_mfi:
            logger_with_extra_info.warning(
                f'Not dropping {raw_code} antibody: '
                f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                f'To be consulted with immunologist, because the antibody is NOT dropped even though there are some MFI'
                f' values below cutoff.'
            )

        elif relevant_mean < cutoff and only_one_number_used:
            logger_with_extra_info.warning(
                f'Dropping {raw_code} antibody: '
                f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                f'To be consulted with immunologist, because the antibody is dropped even though only one MFI value was'
                f' identified as relevant for the MFI calculatuion and therefore the final calculated mean is less '
                f'relevant.'
            )

        return int(relevant_mean)
    return int(np.mean(mfis))
