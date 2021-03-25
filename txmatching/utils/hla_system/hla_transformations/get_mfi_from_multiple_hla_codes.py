from typing import List

import numpy as np

from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_transformations.parsing_error import \
    add_parsing_error_to_db_session
from txmatching.utils.logging_tools import ParsingInfo

RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI = 1

RELATIVE_CLOSENESS_TO_CUTOFF_FROM_BELOW = 0.5
RELATIVE_CLOSENESS_TO_CUTOFF_FROM_ABOVE = 1.25
RELATIVE_CLOSENESS_TO_MINIMUM = 1 / 2


def get_mfi_from_multiple_hla_codes(mfis: List[int],
                                    cutoff: int,
                                    raw_code: str,
                                    parsing_info: ParsingInfo = None) -> int:
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
            add_parsing_error_to_db_session(
                raw_code, HlaCodeProcessingResultDetail.MFI_PROBLEM,
                f'Dropping {raw_code} antibody: '
                f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                f'To be consulted with immunologist, because the antibody is dropped even though it has some high MFI '
                f'values.',
                parsing_info
            )

        elif relevant_mean > cutoff > min_mfi:
            add_parsing_error_to_db_session(
                raw_code, HlaCodeProcessingResultDetail.MFI_PROBLEM,
                f'Not dropping {raw_code} antibody: '
                f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                f'To be consulted with immunologist, because the antibody is NOT dropped even though there are some MFI'
                f' values below cutoff.',
                parsing_info
            )

        elif relevant_mean < cutoff and only_one_number_used:
            add_parsing_error_to_db_session(
                raw_code, HlaCodeProcessingResultDetail.MFI_PROBLEM,
                f'Dropping {raw_code} antibody: '
                f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                f'To be consulted with immunologist, because the antibody is dropped even though only one MFI value was'
                f' identified as relevant for the MFI calculation and therefore the final calculated mean is less '
                f'relevant.',
                parsing_info
            )

        return int(relevant_mean)
    return int(np.mean(mfis))
