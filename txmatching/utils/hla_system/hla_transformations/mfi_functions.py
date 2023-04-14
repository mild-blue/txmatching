from typing import Dict, List, Optional, Tuple

import numpy as np

from txmatching.data_transfer_objects.hla.parsing_issue_dto import \
    ParsingIssueBase
from txmatching.patients.hla_model import HLAAntibody
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail

RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI = 3 / 4

RELATIVE_CLOSENESS_TO_CUTOFF_FROM_BELOW = 3 / 4
RELATIVE_CLOSENESS_TO_CUTOFF_FROM_ABOVE = 1.25
RELATIVE_CLOSENESS_TO_MINIMUM = 1 / 2
DIFFERENCE_THRESHOLD_RATIO = 1 / 4

MAX_MFI_RATIO_TO_BE_JUST_BELOW_CUTOFF = 7 / 8


# The function below shoud not be used. It is kept only to make txmatching be able to process old data.
def get_mfi_from_multiple_hla_codes_single_chain(mfis: List[int],
                                                 cutoff: int,
                                                 raw_code: str) -> Tuple[List[ParsingIssueBase], int]:
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
    # if there is just one MFI value, simply return it
    if len(mfis) == 1:
        return [], mfis[0]
    mfis = np.array(mfis)
    max_mfi = np.max(mfis)
    min_mfi = np.min(mfis)

    parsing_issues_temp = []

    if min_mfi < 0:
        raise AssertionError(f'MFI has to be always >=0. The data shall be validated on input. Obtained MFI={min_mfi}.')

    max_min_relative_difference = (max_mfi - min_mfi) / min_mfi if min_mfi > 0 else max_mfi
    difference_over_threshold = (max_mfi - min_mfi) > DIFFERENCE_THRESHOLD_RATIO * cutoff

    only_one_number_used = False
    if max_min_relative_difference > RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI and difference_over_threshold:
        mfis_under_mean = mfis[mfis < np.mean(mfis)]
        mfis_close_to_minimum = mfis[mfis < min_mfi + cutoff * RELATIVE_CLOSENESS_TO_MINIMUM]
        # expected case: the low MFIs are identified both as close to minimum and below average. And it is not just one
        # value. Should happen in the case there are two prominent groups of MFIs with large gap.
        if np.array_equal(mfis_under_mean, mfis_close_to_minimum):
            relevant_mean = int(np.mean(mfis_under_mean))
            # Only one value is present in the low batch. This decreases credibility of the result,
            # the value is used anyway (as instructed by immunologist) but this info is added to the warning message.
            if len(mfis_under_mean) == 1:
                only_one_number_used = True

        # In case the two sets of lowest MFIs (MFIs below average and close to minimum) are different, use the
        # batch that is smaller (assuming that there are multiple groups of MFIs and just one of the methods has
        # identified it).
        elif len(min(mfis_under_mean, mfis_close_to_minimum, key=len)) > 1:
            relevant_mean = int(np.mean(min(mfis_under_mean, mfis_close_to_minimum, key=len)))
        # Smallest batch contains only 1 MFI. Taking the large one to make the result more reliable.
        else:
            relevant_mean = int(np.mean(max(mfis_under_mean, mfis_close_to_minimum, key=len)))

    else:
        relevant_mean = int(np.mean(mfis))

    if RELATIVE_CLOSENESS_TO_CUTOFF_FROM_BELOW * cutoff < relevant_mean < cutoff and \
            max_mfi > cutoff * MAX_MFI_RATIO_TO_BE_JUST_BELOW_CUTOFF:
        parsing_issues_temp.append(
            ParsingIssueBase(
                hla_code_or_group=raw_code,
                parsing_issue_detail=ParsingIssueDetail.MFI_PROBLEM,
                message=f'Dropping {raw_code} antibody: '
                        f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                        f'To be consulted with immunologist, the estimated overall MFI is below cutoff, but the '
                        f'value is close to cutoff.'
            )
        )

    elif relevant_mean > cutoff > min_mfi:
        parsing_issues_temp.append(
            ParsingIssueBase(
                hla_code_or_group=raw_code,
                parsing_issue_detail=ParsingIssueDetail.MFI_PROBLEM,
                message=f'Not dropping {raw_code} antibody: '
                        f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                        f'To be consulted with immunologist, because the antibody is NOT dropped even though '
                        f'there are some MFI values below cutoff.'
            )
        )

    elif relevant_mean < cutoff and only_one_number_used and max_mfi > cutoff * MAX_MFI_RATIO_TO_BE_JUST_BELOW_CUTOFF:
        parsing_issues_temp.append(
            ParsingIssueBase(
                hla_code_or_group=raw_code,
                parsing_issue_detail=ParsingIssueDetail.MFI_PROBLEM,
                message=f'Dropping {raw_code} antibody: '
                        f'Calculated MFI: {int(relevant_mean)}, Cutoff: {cutoff}, MFI values: {mfis}. '
                        f'To be consulted with immunologist, because the antibody is dropped even though only'
                        f' one MFI value was identified as relevant for the MFI calculation and therefore '
                        f'the final calculated mean is less relevant.'
            )
        )

    return parsing_issues_temp, relevant_mean


def is_positive_mfi_present(raw_code: str, mfi_dictionary: Dict[str, List[int]], cutoff: int) -> bool:
    for mfi in mfi_dictionary[raw_code]:
        if mfi >= cutoff:
            return True
    return False


def is_only_one_positive_mfi_present(raw_code: str, mfi_dictionary: Dict[str, List[int]], cutoff: int) -> bool:
    positive_mfis = [mfi for mfi in mfi_dictionary[raw_code] if mfi >= cutoff]
    return len(positive_mfis) == 1


def is_negative_mfi_present(raw_code: str, mfi_dictionary: Dict[str, List[int]], cutoff: int) -> bool:
    for mfi in mfi_dictionary[raw_code]:
        if mfi < cutoff:
            return True
    return False


def get_average_mfi(raw_code: str, mfi_dictionary: Dict[str, List[int]], _: Optional[int]) -> int:
    return int(np.mean(np.array(mfi_dictionary[raw_code])))


def get_negative_average_mfi(raw_code: str, mfi_dictionary: Dict[str, List[int]], cutoff: int) -> int:
    mfis = np.array([mfi for mfi in mfi_dictionary[raw_code] if mfi < cutoff])
    return int(np.mean(mfis))


def get_positive_average_mfi(raw_code: str, mfi_dictionary: Dict[str, List[int]], cutoff: int) -> int:
    mfis = np.array([mfi for mfi in mfi_dictionary[raw_code] if mfi >= cutoff])
    return int(np.mean(mfis))


def create_mfi_dictionary(antibody_list_double_code: List[HLAAntibody]) -> Dict[str, List[int]]:
    mfi_dictionary = {}
    for antibody in antibody_list_double_code:
        if antibody.raw_code not in mfi_dictionary:
            mfi_dictionary[antibody.raw_code] = [antibody.mfi]
        else:
            mfi_dictionary[antibody.raw_code].append(antibody.mfi)
        if antibody.second_raw_code not in mfi_dictionary:
            mfi_dictionary[antibody.second_raw_code] = [antibody.mfi]
        else:
            mfi_dictionary[antibody.second_raw_code].append(antibody.mfi)

    return mfi_dictionary
