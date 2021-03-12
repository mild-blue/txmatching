import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set, Union

import numpy as np

from txmatching.patients.hla_code import HLACode
from txmatching.utils.hla_system.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_table import (ALL_SPLIT_BROAD_CODES,
                                                   BROAD_CODES, SPLIT_CODES,
                                                   SPLIT_TO_BROAD)
from txmatching.utils.hla_system.rel_dna_ser_exceptions import (
    PARSE_HLA_CODE_EXCEPTIONS,
    PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES)
from txmatching.utils.hla_system.rel_dna_ser_parsing import \
    HIGH_RES_TO_SPLIT_OR_BROAD

logger = logging.getLogger(__name__)

RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI = 1

RELATIVE_CLOSENESS_TO_CUTOFF_FROM_BELOW = 0.5
RELATIVE_CLOSENESS_TO_CUTOFF_FROM_ABOVE = 1.25
RELATIVE_CLOSENESS_TO_MINIMUM = 1 / 2

LOW_RES_REGEX = re.compile(r'^[A-Z]+\d?\*\d{2,4}$')
ULTRA_HIGH_RES_REGEX = re.compile(r'^([A-Z]+\d?\*\d{2,4}(:\d{2,3}))(:\d{2,3})+[A-Z]?$')  # with high res subunit
HIGH_RES_REGEX = re.compile(r'^[A-Z]+\d?\*\d{2,4}(:\d{2,3})[A-Z]?$')
HIGH_RES_REGEX_ENDING_WITH_N = re.compile(r'^[A-Z]+\d?\*\d{2,4}(:\d{2,3})N$')
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
    maybe_hla_code: Optional[HLACode]
    result_detail: HlaCodeProcessingResultDetail


def _try_convert_ultra_high_res(high_res_or_ultra_high_res: str) -> Optional[str]:
    if HIGH_RES_REGEX.match(high_res_or_ultra_high_res):
        return high_res_or_ultra_high_res

    match = ULTRA_HIGH_RES_REGEX.search(high_res_or_ultra_high_res)
    if match:
        high_res = match.group(1)
        assert HIGH_RES_REGEX.match(high_res)
        return high_res
    else:
        return None


def _ultra_high_res_to_high_res_with_check(ultra_high_res_code: str) -> Union[str, HlaCodeProcessingResultDetail]:
    # Check that the code can be converted to split
    expected_split_or_broad = _high_res_to_split_or_broad(ultra_high_res_code)
    if isinstance(expected_split_or_broad, HlaCodeProcessingResultDetail):
        return expected_split_or_broad

    # Convert ultra high res -> high res
    high_res = _try_convert_ultra_high_res(ultra_high_res_code)
    assert high_res is not None, f'Code ${ultra_high_res_code} is not in ultra high resolution'

    # Get splits corresponding to this high res substring
    split_to_high_res = dict()
    for high_res_or_ultra_high_res, split_or_broad in HIGH_RES_TO_SPLIT_OR_BROAD.items():
        if split_or_broad is None:
            continue
        maybe_high_res = _try_convert_ultra_high_res(high_res_or_ultra_high_res)
        if maybe_high_res is not None and high_res == maybe_high_res:
            if split_or_broad not in split_to_high_res:
                split_to_high_res[split_or_broad] = []
            split_to_high_res[split_or_broad].append(high_res_or_ultra_high_res)

    assert len(split_to_high_res) > 0

    # If all high res variants are converted to the same split, there is no problem and return the high_res
    if len(split_to_high_res) == 1:
        assert expected_split_or_broad in next(iter(split_to_high_res))
        return high_res
    else:
        # This should not happen. See test_no_ultra_high_res_with_multiple_splits
        raise AssertionError(f'Ultra high res {ultra_high_res_code} converted to high res {high_res} which '
                             f'corresponds to ultra high res codes that can be converted to multiple split '
                             f'codes: ${split_to_high_res}')


def _get_possible_splits_for_high_res_code(high_res_code: str) -> Set[str]:
    return {split for high_res, split in HIGH_RES_TO_SPLIT_OR_BROAD.items() if
            high_res.startswith(f'{high_res_code}:') or high_res == high_res_code}


def _high_res_to_split_or_broad(high_res_code: str) -> Union[str, HlaCodeProcessingResultDetail]:
    """
    Transforms high resolution code to serological (split) code or broad code. In the case no code is found
    HlaCodeProcessingResultDetail with details is returned.
    :param high_res_code: High res code to transform.
    :return: Either found split code or broad code or HlaCodeProcessingResultDetail in case no code is found.
    """
    maybe_split_or_broad = HIGH_RES_TO_SPLIT_OR_BROAD.get(
        high_res_code, _get_possible_splits_for_high_res_code(high_res_code))
    if maybe_split_or_broad is None:
        # Code found in the HIGH_RES_TO_SPLIT_OR_BROAD but none was returned as the transformation is unknown.
        return HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES
    elif isinstance(maybe_split_or_broad, str):
        return maybe_split_or_broad
    else:
        assert isinstance(maybe_split_or_broad, set), 'Unexpected type'
        if len(maybe_split_or_broad) == 0:
            # No code found in HIGH_RES_TO_SPLIT_OR_BROAD so it is code in high_res_code that does not exist in our
            # transformation table at all.
            return HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE
        possible_split_or_broad_resolutions = maybe_split_or_broad.difference({None})
        if len(possible_split_or_broad_resolutions) == 0:
            return HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES
        else:
            found_splits = set(possible_split_or_broad_resolutions)
            if len(found_splits) == 1:
                return possible_split_or_broad_resolutions.pop()
            else:
                # in case there are multiple possibilities we do not know which to choose and return None.
                logger.warning(f'Multiple possible split or broad resolutions for high res code {high_res_code}'
                               f' found: {possible_split_or_broad_resolutions}')
                return HlaCodeProcessingResultDetail.MULTIPLE_SPLITS_OR_BROADS_FOUND


# I think that many return statements and many branches are meaningful here
# pylint: disable=too-many-return-statements, too-many-branches
def parse_hla_raw_code_with_details(hla_raw_code: str) -> HlaCodeProcessingResult:
    # firstly, if raw code is in hla code exceptions list, create parsing result
    maybe_exception_split_code = PARSE_HLA_CODE_EXCEPTIONS.get(hla_raw_code)
    if maybe_exception_split_code:
        return HlaCodeProcessingResult(
            HLACode(
                high_res=hla_raw_code,
                split=maybe_exception_split_code,
                broad=split_to_broad(maybe_exception_split_code)
            ),
            HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED
        )

    if re.match(LOW_RES_REGEX, hla_raw_code):
        high_res = None
        split_or_broad_or_error = _high_res_to_split_or_broad(hla_raw_code)
        logger.warning(f'Low res code {hla_raw_code} parsed as split code {split_or_broad_or_error}')
    elif re.match(HIGH_RES_REGEX, hla_raw_code):
        high_res = hla_raw_code
        split_or_broad_or_error = _high_res_to_split_or_broad(hla_raw_code)
    elif re.match(ULTRA_HIGH_RES_REGEX, hla_raw_code):
        high_res_or_error = _ultra_high_res_to_high_res_with_check(hla_raw_code)
        if not isinstance(high_res_or_error, HlaCodeProcessingResultDetail):
            assert re.match(HIGH_RES_REGEX, high_res_or_error)
            logger.warning(f'Ultra high resolution {hla_raw_code} parsed as high resolution {high_res_or_error}')
            high_res = high_res_or_error
            split_or_broad_or_error = _high_res_to_split_or_broad(hla_raw_code)
        else:
            return HlaCodeProcessingResult(None, high_res_or_error)
    else:
        high_res = None
        split_or_broad_or_error = hla_raw_code

    if not isinstance(split_or_broad_or_error, HlaCodeProcessingResultDetail) and \
            re.match(SPLIT_RES_REGEX, split_or_broad_or_error):
        c_match = re.match(CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX, split_or_broad_or_error)
        if c_match:
            split_or_broad_or_error = f'CW{int(c_match.group(1))}'

        b_match = re.match(B_SEROLOGICAL_CODE_WITH_W_REGEX, split_or_broad_or_error)
        if b_match:
            # doesn't actually do anything atm, but Bw is a special kind of antigen so we want to keep the branch here
            split_or_broad_or_error = f'BW{int(b_match.group(1))}'

        dpqb_match = re.match(DQ_DP_SEROLOGICAL_CODE_WITH_AB_REGEX, split_or_broad_or_error)
        if dpqb_match:
            subtype_str = 'A' if dpqb_match.group(2) == 'A' else ''
            split_or_broad_or_error = f'{dpqb_match.group(1)}{subtype_str}{int(dpqb_match.group(3))}'

        if split_or_broad_or_error in SPLIT_CODES:
            # Raw code was high res or split
            return HlaCodeProcessingResult(
                HLACode(
                    high_res=high_res,
                    split=split_or_broad_or_error,
                    broad=split_to_broad(split_or_broad_or_error)
                ),
                HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED
            )
        elif split_or_broad_or_error in BROAD_CODES:
            # Raw code was broad
            if high_res is None:
                return HlaCodeProcessingResult(
                    HLACode(
                        high_res=None,
                        split=None,
                        broad=split_or_broad_or_error
                    ),
                    HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED
                )
            # Raw code was high res
            else:
                return HlaCodeProcessingResult(
                    HLACode(
                        high_res=high_res,
                        split=None,
                        broad=split_or_broad_or_error
                    ),
                    HlaCodeProcessingResultDetail.HIGH_RES_WITHOUT_SPLIT
                )
        else:
            # Some split HLA codes are missing in our table, therefore we still return the found HLA code if it matches
            # expected format of split codes. In this case split = broad.
            return HlaCodeProcessingResult(
                HLACode(
                    high_res=high_res,
                    split=split_or_broad_or_error,
                    broad=split_or_broad_or_error
                ),
                HlaCodeProcessingResultDetail.UNEXPECTED_SPLIT_RES_CODE
            )

    elif isinstance(split_or_broad_or_error, HlaCodeProcessingResultDetail):
        return HlaCodeProcessingResult(None, split_or_broad_or_error)
    else:
        return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)


def parse_hla_raw_code(hla_raw_code: str) -> HLACode:
    """
    This method is used in tests and should never be used in other code. For that, please use
    parse_hla_raw_code_and_store_parsing_error_in_db. These two method are partially redundant so in case of update,
    update the second one too.
    :param hla_raw_code:
    :return: parsed raw code
    """
    logger.debug('Parsing HLA code')
    parsing_result = parse_hla_raw_code_with_details(hla_raw_code)
    if not parsing_result.maybe_hla_code:
        raise ValueError(f'HLA code processing of {hla_raw_code} was not successful: {parsing_result.result_detail}')
    if parsing_result.result_detail != HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED:
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


def get_mfi_from_multiple_hla_codes(mfis: List[int],
                                    cutoff: int,
                                    raw_code: str,
                                    logger_with_extra_info: Union[
                                        logging.Logger, logging.LoggerAdapter] = logging.getLogger(__name__)) -> int:
    """
    Takes list of MFIs of the same hla code and estimates the MFI for the code.
    It is based on discussions with immunologists. If variance is low, take average, if variance is high, take average
    only of the lower portion of MFIs. If the calculated average is close to cutoff raise warning, each of such cases is
    to be checked by immunologist.

    The reason some antibodies occur multiple times is because antibodies existence is tested together for alpha and
    beta alleles. And we need to distinguish whether the MFI value relates to alpha or beta or both.

    To identify large variance two conditions have to be fulfilled:
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

    max_min_relative_difference = (max_mfi - min_mfi) / min_mfi if min_mfi > 0 else max_mfi
    difference_over_cutoff = (max_mfi - min_mfi) > cutoff

    only_one_number_used = False
    if max_min_relative_difference > RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI and difference_over_cutoff:
        mfis_under_mean = mfis[mfis < np.mean(mfis)]
        mfis_close_to_minimum = mfis[mfis < min_mfi + cutoff * RELATIVE_CLOSENESS_TO_MINIMUM]
        # expected case: the low MFIs are identified both as close to minimum and below average. And it is not just one
        # value. Should happen in the case there are two prominent groups of MFIs with large gap.
        if np.array_equal(mfis_under_mean, mfis_close_to_minimum):
            relevant_mean = np.mean(mfis_under_mean)
            # Only one value is present in the low batch. This decreases credibility of the result,
            # the value is used anyway (as instructed by immunologist) but this info is added to the warning message.
            if len(mfis_under_mean) == 1:
                only_one_number_used = True

        # In case the two sets of lowest MFIs (MFIs below average and close to minimum) are different, use the
        # batch that is smaller (assuming that there are multiple groups of MFIs and just one of the methods has
        # identified it).
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
                f' identified as relevant for the MFI calculation and therefore the final calculated mean is less '
                f'relevant.'
            )

        return int(relevant_mean)
    return int(np.mean(mfis))
