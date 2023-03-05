import itertools
import logging
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union

from txmatching.data_transfer_objects.hla.parsing_issue_dto import \
    ParsingIssueBase
from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibody, HLAAntibodyType,
                                           HLAPerGroup, HLAType)
from txmatching.utils.constants import \
    SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES
from txmatching.utils.enums import (HLA_GROUPS,
                                    HLA_GROUPS_OTHER, HLA_GROUPS_PROPERTIES,
                                    HLAGroup)
from txmatching.utils.hla_system.hla_transformations.mfi_functions import (create_mfi_dictionary,
                                                                           get_average_mfi,
                                                                           get_mfi_from_multiple_hla_codes_single_chain,
                                                                           get_negative_average_mfi,
                                                                           is_negative_mfi_present,
                                                                           is_only_one_positive_mfi_present,
                                                                           is_positive_mfi_present)
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.utils.hla_system.rel_dna_ser_exceptions import \
    MULTIPLE_SERO_CODES_LIST

logger = logging.getLogger(__name__)


@dataclass
class HighResAntibodiesAnalysis:
    is_type_a_compliant: bool
    maybe_parsing_issue: Optional[ParsingIssueDetail]


def split_hla_types_to_groups(hla_types: List[HLAType]) -> Tuple[List[ParsingIssueBase], List[HLAPerGroup]]:
    parsing_issues, hla_types_in_groups = _split_hla_types_to_groups(hla_types)
    return (parsing_issues, [HLAPerGroup(hla_group,
                                         sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                                         ) for hla_group, hla_codes_in_group in
                             hla_types_in_groups.items()])


def split_hla_types_to_groups_other(
        hla_types: List[HLAType]
) -> Tuple[List[ParsingIssueBase], Dict[HLAGroup, List[HLAType]]]:
    parsing_issues = []
    hla_types_in_groups = {}
    for hla_group in HLA_GROUPS_OTHER:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_types:
        for hla_group in HLA_GROUPS_OTHER:
            if _is_hla_type_in_group(hla_type, hla_group):
                hla_types_in_groups[hla_group] += [hla_type]
                break
    return (parsing_issues, hla_types_in_groups)


def create_hla_antibodies_per_groups_from_hla_antibodies(
        hla_antibodies: List[HLAAntibody],
) -> Tuple[List[ParsingIssueBase], List[AntibodiesPerGroup]]:
    antibodies_parsing_issues, hla_antibodies_joined = _join_duplicate_antibodies(hla_antibodies)
    antibodies_per_groups_parsing_issues, hla_antibodies_per_groups = _split_antibodies_to_groups(hla_antibodies_joined)

    parsing_issues = antibodies_parsing_issues + antibodies_per_groups_parsing_issues
    return (parsing_issues, hla_antibodies_per_groups)


def _split_antibodies_to_groups(hla_antibodies: List[HLAAntibody]) -> Tuple[
        List[ParsingIssueBase], List[AntibodiesPerGroup]]:
    parsing_issues, hla_antibodies_in_groups = _split_hla_types_to_groups(hla_antibodies)
    return (parsing_issues, [AntibodiesPerGroup(hla_group,
                                                sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                                                ) for hla_group, hla_codes_in_group in
                             hla_antibodies_in_groups.items()])


def _join_duplicate_antibodies(
        hla_antibodies: List[HLAAntibody]
) -> Tuple[List[ParsingIssueBase], List[HLAAntibody]]:

    # divide antibodies into single and double coded
    antibody_list_single_code = [
        hla_antibody for hla_antibody in hla_antibodies if hla_antibody.second_raw_code is None]
    antibody_list_double_code = [
        hla_antibody for hla_antibody in hla_antibodies if hla_antibody.second_raw_code is not None]

    single_antibodies_parsing_issues, single_antibodies_joined = _add_single_hla_antibodies(antibody_list_single_code)

    double_antibodies_parsing_issues, double_antibodies_joined = _add_double_hla_antibodies(antibody_list_double_code,
                                                                                            single_antibodies_joined)

    parsing_issues = single_antibodies_parsing_issues + double_antibodies_parsing_issues
    hla_antibodies_joined = double_antibodies_joined

    return parsing_issues, hla_antibodies_joined


def _add_single_hla_antibodies(antibody_list_single_code: List[HLAAntibody]) -> Tuple[List[ParsingIssueBase], List[HLAAntibody]]:
    def _group_key(hla_antibody: HLAAntibody) -> str:
        return hla_antibody.raw_code

    parsing_issues = []
    hla_antibodies_joined = []

    grouped_single_hla_antibodies = itertools.groupby(sorted(antibody_list_single_code, key=_group_key), key=_group_key)

    for hla_code_raw, antibody_group in grouped_single_hla_antibodies:
        antibody_group_list = list(antibody_group)
        cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group_list}
        if len(cutoffs) != 1:
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=hla_code_raw,
                    parsing_issue_detail=ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY,
                    message=ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY.value
                )
            )
            continue

        cutoff = cutoffs.pop()
        # if a single antibody is present multiple times, parse it but throw an error message
        if len(antibody_group_list) > 1:
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=hla_code_raw,
                    parsing_issue_detail=ParsingIssueDetail.DUPLICATE_ANTIBODY_SINGLE_CHAIN,
                    message=ParsingIssueDetail.DUPLICATE_ANTIBODY_SINGLE_CHAIN.value
                )
            )
        # add the single antibody using the old logic
        mfi_parsing_issues, mfi = get_mfi_from_multiple_hla_codes_single_chain(
            [hla_code.mfi for hla_code in antibody_group_list], cutoff, hla_code_raw)
        parsing_issues = parsing_issues + mfi_parsing_issues
        new_antibody = HLAAntibody(
            code=antibody_group_list[0].code,
            raw_code=hla_code_raw,
            cutoff=cutoff,
            mfi=mfi
        )
        hla_antibodies_joined.append(new_antibody)

    return parsing_issues, hla_antibodies_joined


# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks
def _add_double_hla_antibodies(antibody_list_double_code: List[HLAAntibody],
                               single_antibodies_joined: List[HLAAntibody]) -> \
        Tuple[List[ParsingIssueBase], List[HLAAntibody]]:

    mfi_dictionary = create_mfi_dictionary(antibody_list_double_code)

    # TODO check multiple cutoffs

    parsing_issues = []
    hla_antibodies_joined = single_antibodies_joined.copy()

    # iterate over all double antibodies
    for double_antibody in antibody_list_double_code:
        parsed_hla_codes = set([antibody.raw_code for antibody in hla_antibodies_joined] + [
            antibody.second_raw_code for antibody in hla_antibodies_joined if antibody.second_raw_code is not None])

        # if both codes are already parsed, skip this double antibody
        if not {double_antibody.raw_code, double_antibody.second_raw_code}.issubset(parsed_hla_codes):
            # if MFI is under cutoff, for both chains check whether there is a positive MFI elsewhere,
            # if not, return the mean MFI
            if double_antibody.mfi < double_antibody.cutoff:
                # check alpha chain
                if not is_positive_mfi_present(double_antibody.raw_code, mfi_dictionary,
                                               double_antibody.cutoff) and double_antibody.raw_code not in parsed_hla_codes:
                    hla_antibodies_joined.append(_create_alpha_chain_antibody(
                        double_antibody, get_average_mfi, mfi_dictionary))
                # check beta chain
                if not is_positive_mfi_present(double_antibody.second_raw_code, mfi_dictionary,
                                               double_antibody.cutoff) and double_antibody.second_raw_code not in parsed_hla_codes:
                    hla_antibodies_joined.append(_create_beta_chain_antibody(
                        double_antibody, get_average_mfi, mfi_dictionary))
            else:
                alpha_chain_only_positive = not is_negative_mfi_present(
                    double_antibody.raw_code, mfi_dictionary, double_antibody.cutoff)
                beta_chain_only_positive = not is_negative_mfi_present(
                    double_antibody.second_raw_code, mfi_dictionary, double_antibody.cutoff)
                # if both chains have only positive MFIs, compute average MFI for each separately
                if alpha_chain_only_positive and beta_chain_only_positive:
                    # alpha chain
                    if double_antibody.raw_code not in parsed_hla_codes:
                        hla_antibodies_joined.append(_create_alpha_chain_antibody(
                            double_antibody, get_average_mfi, mfi_dictionary))
                    # beta chain
                    if double_antibody.second_raw_code not in parsed_hla_codes:
                        hla_antibodies_joined.append(_create_beta_chain_antibody(
                            double_antibody, get_average_mfi, mfi_dictionary))
                # if one is positive and one is mixed
                elif alpha_chain_only_positive != beta_chain_only_positive:
                    if alpha_chain_only_positive:
                        if double_antibody.raw_code not in parsed_hla_codes:
                            hla_antibodies_joined.append(_create_alpha_chain_antibody(
                                double_antibody, get_average_mfi, mfi_dictionary))
                        if is_only_one_positive_mfi_present(double_antibody.second_raw_code, mfi_dictionary,
                            double_antibody.cutoff) and double_antibody.second_raw_code not in parsed_hla_codes:
                            hla_antibodies_joined.append(_create_beta_chain_antibody(
                                double_antibody, get_negative_average_mfi, mfi_dictionary))

                    if beta_chain_only_positive:
                        if double_antibody.second_raw_code not in parsed_hla_codes:
                            hla_antibodies_joined.append(_create_beta_chain_antibody(
                                double_antibody, get_average_mfi, mfi_dictionary))
                        if is_only_one_positive_mfi_present(double_antibody.raw_code, mfi_dictionary,
                            double_antibody.cutoff) and double_antibody.raw_code not in parsed_hla_codes:
                            hla_antibodies_joined.append(_create_alpha_chain_antibody(
                                double_antibody, get_negative_average_mfi, mfi_dictionary))

                # if both are mixed add double antibody
                else:
                    # add double antibody and parsing issue
                    hla_antibodies_joined.append(double_antibody)
                    parsing_issues.append(
                        ParsingIssueBase(
                            hla_code_or_group=double_antibody.raw_code + ", " + double_antibody.second_raw_code,
                            parsing_issue_detail=ParsingIssueDetail.DUPLICATE_ANTIBODY_SINGLE_CHAIN,
                            message=ParsingIssueDetail.DUPLICATE_ANTIBODY_SINGLE_CHAIN.value
                        )
                    )
                    # TODO: maju sa pridat aj ked uz su sparsovane v pripade theoretical hej?
                    # add theoretical alpha chain with averaged MFI
                    hla_antibodies_joined.append(_create_alpha_chain_antibody(
                        double_antibody, get_average_mfi, mfi_dictionary, HLAAntibodyType.THEORETICAL))
                    # add theoretical betas chain with averaged MFI
                    hla_antibodies_joined.append(_create_beta_chain_antibody(
                        double_antibody, get_average_mfi, mfi_dictionary, HLAAntibodyType.THEORETICAL))

    return parsing_issues, hla_antibodies_joined


HLACodeAlias = Union[HLAType, HLAAntibody]


def _is_hla_type_in_group(hla_type: HLACodeAlias, hla_group: HLAGroup) -> bool:
    if hla_type.code.broad is not None:
        return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].split_code_regex, hla_type.code.broad))
    elif hla_type.code.high_res is not None:
        return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex, hla_type.code.high_res))
    else:
        raise AssertionError(f'Broad or high res should be provided: {hla_type.code}')


def _split_hla_types_to_groups(hla_types: List[HLACodeAlias]) -> Tuple[List[ParsingIssueBase], Dict[HLAGroup,
                                                                                                    List[
                                                                                                        HLACodeAlias]]]:
    parsing_issues = []
    hla_types_in_groups = {}
    for hla_group in HLA_GROUPS + [HLAGroup.INVALID_CODES]:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_types:
        match_found = False
        for hla_group in HLA_GROUPS:
            if _is_hla_type_in_group(hla_type, hla_group):
                hla_types_in_groups[hla_group].append(hla_type)
                match_found = True
                break
        if not match_found:
            hla_types_in_groups[HLAGroup.INVALID_CODES].append(hla_type)
    return parsing_issues, hla_types_in_groups


def is_all_antibodies_in_high_res(recipient_antibodies: List[HLAAntibody]) -> bool:
    for antibody in recipient_antibodies:
        # TODO the not in multiple sero codes list is ugly hack, improve in
        #  https://github.com/mild-blue/txmatching/issues/1036
        if antibody.code.high_res is None and antibody.code.split not in MULTIPLE_SERO_CODES_LIST:
            return False
    return True


def analyze_if_high_res_antibodies_are_type_a(
        recipient_antibodies: List[HLAAntibody]) -> HighResAntibodiesAnalysis:
    assert is_all_antibodies_in_high_res(recipient_antibodies), \
        'This method is available just for antibodies in high res.'

    is_some_antibody_below_cutoff = False
    for antibody in recipient_antibodies:
        if antibody.mfi < antibody.cutoff:
            is_some_antibody_below_cutoff = True

    if not is_some_antibody_below_cutoff:
        return HighResAntibodiesAnalysis(False,
                                         ParsingIssueDetail.ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES)
    elif is_some_antibody_below_cutoff and len(recipient_antibodies) < SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES:
        return HighResAntibodiesAnalysis(False,
                                         ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES)
    return HighResAntibodiesAnalysis(True, None)


def _create_alpha_chain_antibody(double_antibody: HLAAntibody,
                                 mfi_function: Callable,
                                 mfi_dictionary: Dict[str, List[int]],
                                 antibody_type: Optional[HLAAntibodyType] = HLAAntibodyType.NORMAL) -> HLAAntibody:
    mfi = mfi_function(double_antibody.raw_code, mfi_dictionary, double_antibody.cutoff)
    return HLAAntibody(
        code=double_antibody.code,
        raw_code=double_antibody.raw_code,
        cutoff=double_antibody.cutoff,
        mfi=mfi,
        type=antibody_type
    )


def _create_beta_chain_antibody(double_antibody: HLAAntibody,
                                mfi_function: Callable,
                                mfi_dictionary: Dict[str, List[int]],
                                antibody_type: Optional[HLAAntibodyType] = HLAAntibodyType.NORMAL) -> HLAAntibody:
    mfi = mfi_function(double_antibody.second_raw_code, mfi_dictionary, double_antibody.cutoff)
    return HLAAntibody(
        code=double_antibody.second_code,
        raw_code=double_antibody.second_raw_code,
        cutoff=double_antibody.cutoff,
        mfi=mfi,
        type=antibody_type
    )
