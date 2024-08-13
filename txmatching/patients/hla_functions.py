import itertools
import logging
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from txmatching.auth.exceptions import ETRLErrorResponse, ETRLRequestException
from txmatching.data_transfer_objects.hla.parsing_issue_dto import \
    ParsingIssueBase
from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibody,
                                           HLAAntibodyForCPRA, HLAPerGroup,
                                           HLAType)
from txmatching.utils.constants import \
    SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES
from txmatching.utils.enums import (HLA_GROUPS, HLA_GROUPS_PROPERTIES,
                                    DQDPChain, HLAAntibodyType, HLAGroup)
from txmatching.utils.hla_system.compatibility_index import _which_dq_dp_chain
from txmatching.utils.hla_system.hla_transformations.mfi_functions import (
    create_mfi_dictionary, get_average_mfi,
    get_mfi_from_multiple_hla_codes_single_chain, get_negative_average_mfi,
    get_positive_average_mfi, is_negative_mfi_present,
    is_last_with_positive_mfi, is_positive_mfi_present)
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


def create_hla_antibodies_per_groups_from_hla_antibodies(hla_antibodies: List[HLAAntibody]
                                                         ) -> Tuple[List[ParsingIssueBase], List[AntibodiesPerGroup]]:
    parsing_issues, hla_antibodies_in_groups = _split_hla_types_to_groups(hla_antibodies)
    antibodies_per_group_joined_sorted = []
    for hla_group, hla_codes_in_group in hla_antibodies_in_groups.items():
        group_parsing_issues, hla_codes_in_group_joined = _join_duplicate_antibodies(hla_codes_in_group)
        parsing_issues += group_parsing_issues
        antibodies_per_group_joined_sorted.append(AntibodiesPerGroup(hla_group,
                                                                     sorted(hla_codes_in_group_joined,
                                                                            key=_sort_key_antibodies_in_group)
                                                                     ))

    return parsing_issues, antibodies_per_group_joined_sorted


def _sort_key_antibodies_in_group(antibody: HLAAntibody) -> Tuple[str, str]:
    return antibody.raw_code, antibody.second_raw_code if antibody.second_raw_code is not None else ''


def _join_duplicate_antibodies(
        hla_antibodies: List[HLAAntibody]
) -> Tuple[List[ParsingIssueBase], List[HLAAntibody]]:
    cutoff_parsing_issues = _check_groups_for_multiple_cutoffs(hla_antibodies)

    # divide antibodies into single and double coded
    antibody_list_single_code = [
        hla_antibody for hla_antibody in hla_antibodies if hla_antibody.second_raw_code is None]
    antibody_list_double_code = [
        hla_antibody for hla_antibody in hla_antibodies if hla_antibody.second_raw_code is not None]

    single_antibodies_parsing_issues, single_antibodies_joined = _add_single_hla_antibodies(antibody_list_single_code)

    double_antibodies_parsing_issues, double_antibodies_joined = _add_double_hla_antibodies(antibody_list_double_code,
                                                                                            single_antibodies_joined)

    parsing_issues = single_antibodies_parsing_issues + double_antibodies_parsing_issues + cutoff_parsing_issues

    return parsing_issues, double_antibodies_joined


def _check_groups_for_multiple_cutoffs(hla_antibodies: List[HLAAntibody]) -> List[ParsingIssueBase]:
    # divide antibodies to groups
    split_antibodies = _split_hla_types_to_groups(hla_antibodies)[1]
    cutoff_parsing_issues = []
    # check if there are multiple cutoffs
    for hla_group, antibody_group_list in split_antibodies.items():
        cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group_list}
        if len(cutoffs) > 1:
            cutoff_parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=hla_group,
                    parsing_issue_detail=ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_GROUP,
                    message=ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_GROUP.value
                )
            )
            continue
    return cutoff_parsing_issues


def _add_single_hla_antibodies(antibody_list_single_code: List[HLAAntibody]) -> Tuple[
        List[ParsingIssueBase], List[HLAAntibody]]:
    def _group_key(hla_antibody: HLAAntibody) -> str:
        return hla_antibody.raw_code

    parsing_issues = []
    hla_antibodies_joined = []

    grouped_single_hla_antibodies = itertools.groupby(sorted(antibody_list_single_code, key=_group_key), key=_group_key)

    for hla_code_raw, antibody_group in grouped_single_hla_antibodies:
        antibody_group_list = list(antibody_group)

        if len(antibody_group_list) == 1:
            mfi = antibody_group_list[0].mfi
            cutoff = antibody_group_list[0].cutoff
        else:
            # if a single antibody is present multiple times, parse it using the old logic and throw an error message.
            # This is something that should not happen, but we want to be able to parse it anyway. Because it can occur
            # in historical data.
            # in case there are multiple cuttoff it is handled elsewhere. Here we simply take first cutoff
            cutoff = antibody_group_list[0].cutoff
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=hla_code_raw,
                    parsing_issue_detail=ParsingIssueDetail.DUPLICATE_ANTIBODY_SINGLE_CHAIN,
                    message=ParsingIssueDetail.DUPLICATE_ANTIBODY_SINGLE_CHAIN.value
                )
            )
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
# The algorithm scheme is represented in this PDF
# documentation/double_antibodies_parsing/double_antibodies_parsing_algorithm.pdf.
def _add_double_hla_antibodies(antibody_list_double_code: List[HLAAntibody],
                               single_antibodies_joined: List[HLAAntibody]) -> \
        Tuple[List[ParsingIssueBase], List[HLAAntibody]]:
    mfi_dictionary = create_mfi_dictionary(antibody_list_double_code)
    passed_positive_counts_dict: Dict[str, int] = defaultdict(int)

    parsing_issues = []
    hla_antibodies_joined = single_antibodies_joined.copy()

    # iterate over all double antibodies
    for double_antibody in antibody_list_double_code:
        parsed_hla_codes = set([antibody.raw_code for antibody in hla_antibodies_joined] + [
            antibody.second_raw_code for antibody in hla_antibodies_joined if antibody.second_raw_code is not None])

        # if both codes are already parsed, skip this double antibody
        if {double_antibody.raw_code, double_antibody.second_raw_code}.issubset(parsed_hla_codes):
            continue

        # if MFI is under cutoff, for both chains check whether there is a positive MFI elsewhere,
        # if not, return the mean MFI
        if double_antibody.mfi < double_antibody.cutoff:
            hla_antibodies_joined.extend(_parse_double_antibody_mfi_under_cutoff(
                double_antibody, parsed_hla_codes, mfi_dictionary))
        else:
            passed_positive_counts_dict[double_antibody.raw_code] += 1
            passed_positive_counts_dict[double_antibody.second_raw_code] += 1
            alpha_chain_only_positive = not is_negative_mfi_present(
                double_antibody.raw_code, mfi_dictionary, double_antibody.cutoff)
            beta_chain_only_positive = not is_negative_mfi_present(
                double_antibody.second_raw_code, mfi_dictionary, double_antibody.cutoff)
            # if both chains have only positive MFIs, compute average MFI for each separately
            if alpha_chain_only_positive and beta_chain_only_positive:
                _join_both_chains_if_unparsed(double_antibody, hla_antibodies_joined,
                                              parsed_hla_codes, get_average_mfi, mfi_dictionary)

            # if one is positive and one is mixed
            elif alpha_chain_only_positive != beta_chain_only_positive:
                if alpha_chain_only_positive:
                    _join_alpha_chain_if_unparsed(double_antibody, hla_antibodies_joined,
                                                  parsed_hla_codes, get_average_mfi, mfi_dictionary)
                    if is_last_with_positive_mfi(double_antibody.second_raw_code, mfi_dictionary,
                                                 passed_positive_counts_dict[double_antibody.second_raw_code],
                                                 double_antibody.cutoff):
                        # If this is the last positive, and we did not parse, then the positivity
                        # is associated with other chains of these antibodies.
                        # Therefore, we will add it as a negative with the mean of negative MFIs.
                        _join_beta_chain_if_unparsed(double_antibody, hla_antibodies_joined,
                                                     parsed_hla_codes, get_negative_average_mfi, mfi_dictionary)

                if beta_chain_only_positive:
                    _join_beta_chain_if_unparsed(double_antibody, hla_antibodies_joined,
                                                 parsed_hla_codes, get_average_mfi, mfi_dictionary)
                    if is_last_with_positive_mfi(double_antibody.raw_code, mfi_dictionary,
                                                 passed_positive_counts_dict[double_antibody.raw_code],
                                                 double_antibody.cutoff):
                        # If this is the last positive, and we did not parse, then the positivity
                        # is associated with other chains of these antibodies.
                        # Therefore, we will add it as a negative with the mean of negative MFIs.
                        _join_alpha_chain_if_unparsed(double_antibody, hla_antibodies_joined,
                                                      parsed_hla_codes, get_negative_average_mfi, mfi_dictionary)

            # if both are mixed add double antibody
            else:
                theoretical_parsing_issues, theoretical_antibodies = _resolve_theoretical_antibody(
                    double_antibody, parsed_hla_codes, mfi_dictionary, antibody_list_double_code)
                hla_antibodies_joined.extend(theoretical_antibodies)
                parsing_issues.extend(theoretical_parsing_issues)

    return parsing_issues, hla_antibodies_joined


def _resolve_theoretical_antibody(double_antibody: HLAAntibody,
                                  parsed_hla_codes: Set[str],
                                  mfi_dictionary: Dict[str, List[int]],
                                  antibody_list_double_code: List[HLAAntibody]) -> \
        Tuple[List[ParsingIssueBase], List[HLAAntibody]]:
    parsing_issues = []
    hla_antibodies = []

    # add double antibody and parsing issue
    hla_antibodies.append(double_antibody)

    parsing_issues.append(create_parsing_issue_creating_double_antibody(double_antibody, antibody_list_double_code))

    # join theoretical alpha and beta unparsed chains with averaged MFI
    _join_both_chains_if_unparsed(double_antibody, hla_antibodies, parsed_hla_codes,
                                  get_positive_average_mfi, mfi_dictionary, HLAAntibodyType.THEORETICAL)

    return parsing_issues, hla_antibodies


def create_parsing_issue_creating_double_antibody(double_antibody: HLAAntibody,
                                                  antibody_list_double_code: List[HLAAntibody]) -> ParsingIssueBase:
    # extract other occurences of alpha chain
    alpha_chain_occurences = ', '.join([create_raw_code_for_double_antibody(
        antibody) + ' mfi: ' + str(antibody.mfi) for antibody in antibody_list_double_code if
        antibody.code == double_antibody.code and not antibody == double_antibody])

    # extract other occurences of beta chain
    beta_chain_occurences = ', '.join([create_raw_code_for_double_antibody(
        antibody) + ' mfi: ' + str(antibody.mfi) for antibody in antibody_list_double_code if
        antibody.second_code == double_antibody.second_code and not antibody == double_antibody])

    detailed_message = ' The antibody ' + create_raw_code_for_double_antibody(double_antibody) + \
                       ' has positive mfi: ' + str(double_antibody.mfi) + '. Other antibodies with alpha: ' + \
                       alpha_chain_occurences + '. Other antibodies with beta: ' + beta_chain_occurences + '.'

    return ParsingIssueBase(
        hla_code_or_group=create_raw_code_for_double_antibody(double_antibody),
        parsing_issue_detail=ParsingIssueDetail.CREATED_THEORETICAL_ANTIBODY,
        message=ParsingIssueDetail.CREATED_THEORETICAL_ANTIBODY.value + detailed_message
    )


def create_raw_code_for_double_antibody(hla_antibody: HLAAntibody) -> str:
    # Example of HLA antibody raw format: DP[02:01,03:02]
    return hla_antibody.code.high_res[:2] + '[' + hla_antibody.code.high_res.split('*')[1] + ',' + \
        hla_antibody.second_code.high_res.split('*')[1] + ']'


def _parse_double_antibody_mfi_under_cutoff(double_antibody: HLAAntibody,
                                            parsed_hla_codes: Set[str],
                                            mfi_dictionary: Dict[str, List[int]]) -> List[HLAAntibody]:
    hla_antibodies = []

    # check alpha chain
    if not is_positive_mfi_present(double_antibody.raw_code, mfi_dictionary,
                                   double_antibody.cutoff):
        _join_alpha_chain_if_unparsed(double_antibody, hla_antibodies, parsed_hla_codes,
                                      get_average_mfi, mfi_dictionary)

    # check beta chain
    if not is_positive_mfi_present(double_antibody.second_raw_code, mfi_dictionary,
                                   double_antibody.cutoff):
        _join_beta_chain_if_unparsed(double_antibody, hla_antibodies, parsed_hla_codes,
                                     get_average_mfi, mfi_dictionary)

    return hla_antibodies


# pylint: disable=too-many-arguments
def _join_alpha_chain_if_unparsed(double_antibody: HLAAntibody,
                                  joined_antibodies: List[HLAAntibody],
                                  parsed_hla_codes: Set[str],
                                  mfi_function: Callable,
                                  mfi_dictionary: Dict[str, List[int]],
                                  antibody_type: Optional[HLAAntibodyType] = HLAAntibodyType.NORMAL):
    if double_antibody.raw_code in parsed_hla_codes:
        return
    joined_antibodies.append(_create_alpha_chain_antibody(double_antibody,
                                                          mfi_function,
                                                          mfi_dictionary,
                                                          antibody_type))


# pylint: disable=too-many-arguments
def _join_beta_chain_if_unparsed(double_antibody: HLAAntibody,
                                 joined_antibodies: List[HLAAntibody],
                                 parsed_hla_codes: Set[str],
                                 mfi_function: Callable,
                                 mfi_dictionary: Dict[str, List[int]],
                                 antibody_type: Optional[HLAAntibodyType] = HLAAntibodyType.NORMAL):
    if double_antibody.second_raw_code in parsed_hla_codes:
        return
    joined_antibodies.append(_create_beta_chain_antibody(double_antibody,
                                                         mfi_function,
                                                         mfi_dictionary,
                                                         antibody_type))


# pylint: disable=too-many-arguments
def _join_both_chains_if_unparsed(double_antibody: HLAAntibody,
                                  joined_antibodies: List[HLAAntibody],
                                  parsed_hla_codes: Set[str],
                                  mfi_function: Callable,
                                  mfi_dictionary: Dict[str, List[int]],
                                  antibody_type: Optional[HLAAntibodyType] = HLAAntibodyType.NORMAL):
    _join_alpha_chain_if_unparsed(double_antibody, joined_antibodies, parsed_hla_codes,
                                  mfi_function, mfi_dictionary, antibody_type)
    _join_beta_chain_if_unparsed(double_antibody, joined_antibodies, parsed_hla_codes,
                                 mfi_function, mfi_dictionary, antibody_type)


HLACodeAlias = Union[HLAType, HLAAntibody]


def _is_hla_type_in_group(hla_type: HLACodeAlias, hla_group: HLAGroup) -> bool:
    if hla_type.code.broad is not None:
        return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].split_code_regex, hla_type.code.broad))
    elif hla_type.code.high_res is not None:
        return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex, hla_type.code.high_res))
    else:
        raise AssertionError(f'Broad or high res should be provided: {hla_type.code}')


def _split_hla_types_to_groups(hla_types: List[HLACodeAlias]
                               ) -> Tuple[List[ParsingIssueBase], Dict[HLAGroup, List[HLACodeAlias]]]:
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


# pylint: disable=line-too-long
def compute_cpra(unacceptable_antibodies: List[HLAAntibodyForCPRA]) -> float:
    """
    Compute cPRA for unacceptable antibodies with http://ETRL.ORG/.
    We compute cPRA even if the http://ETRL.ORG/ endpoint has VPRA in it,
    but according to the consultation with Matěj Röder, these terms are equivalent for us.
    """
    hla_raw_codes_for_cpra_calculation = [antibody_for_cpra.code_sent_to_calculator for antibody_for_cpra in unacceptable_antibodies]
    etrl_login, etrl_password = os.getenv('ETRL_LOGIN'), os.getenv('ETRL_PASSWORD')
    if not etrl_login or not etrl_password:
        raise ValueError('http://ETRL.ORG/ login or password not found. '
                         'Fill the ETRL_LOGIN and the ETRL_PASSWORD into .env file.')

    url = 'https://www.etrl.org/calculator4.0/calculator4.0.asmx'
    headers = {'content-type': 'text/xml'}
    body = \
        f"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <VirtualPRA xmlns="http://ETRL.ORG/">
                        <sUserName>{etrl_login}</sUserName>
                        <sPassWord>{etrl_password}</sPassWord>
                        <sUnacceptables>{', '.join(hla_raw_codes_for_cpra_calculation)}</sUnacceptables>
                    </VirtualPRA>
                </soap:Body>
            </soap:Envelope>
            """

    try:
        response = requests.post(url, data=body, headers=headers, timeout=15)
        response.raise_for_status()
    except RequestException as ex:
        raise ETRLRequestException(str(ex)) from ex

    soup = BeautifulSoup(response.content, 'xml')

    error_msg = soup.find('ErrorMessage').get_text()
    if error_msg:
        raise ETRLErrorResponse(error_msg)

    cpra = float(soup.find('Frequency').get_text())
    # print(soup.find('matches'))
    # print(soup.find('panelsize'))

    return cpra


def get_unacceptable_antibodies(hla_antibodies) -> List[HLAAntibodyForCPRA]:
    """
    We define an unacceptable antigen as a donor antigen that is considered an absolute
    contraindication for transplantation to a particular patient.
    Such an antigen constitutes a level of immunological risk considered to be appreciably
    greater than the potential benefit to be derived from the transplant.

    source: https://journals.lww.com/co-transplantation/Fulltext/2008/08000/Defining_unacceptable_HLA_antigens.14.aspx
    """
    unacceptable_antibodies = []
    def add_antibody(antibody_str_for_calculation: str) -> None:
        unacceptable_antibodies.append(HLAAntibodyForCPRA(antibody,antibody_str_for_calculation))

    for antibodies_group in hla_antibodies.hla_antibodies_per_groups:
        for antibody in antibodies_group.hla_antibody_list:
            if antibody.type != HLAAntibodyType.NORMAL or \
                    antibody.second_code is not None or \
                    antibody.mfi <= antibody.cutoff:
                # We don't accept double antibodies here, because tool http://ETRL.ORG/
                # for CPRA (VPRA) computation doesn't support them.
                # So we agreed with IKEM to ignore such antibodies
                continue

            if antibodies_group.hla_group not in [HLAGroup.DP, HLAGroup.DQ] or \
                    antibody.code.is_in_high_res():
                # used with the same nomenclature we use
                add_antibody(antibody.code.display_code)
            else:
                # solve different nomenclature of DPA, DPB, DQA, DQB
                dq_dp_chain = _which_dq_dp_chain(antibody)

                if dq_dp_chain == DQDPChain.BETA_DP:
                    hla_number = antibody.code.broad[2:]

                    if len(hla_number) == 1:
                        add_antibody('DP-0' + hla_number)
                    elif len(hla_number) == 2:
                        add_antibody('DP-' + hla_number)
                    else:
                        raise AssertionError

                    if unacceptable_antibodies[-1] == 'DP-02':
                        unacceptable_antibodies[-1] = 'DP-0201'
                        add_antibody('DP-0202')

                    if unacceptable_antibodies[-1] == 'DP-04':
                        unacceptable_antibodies[-1] = 'DP-0401'
                        add_antibody('DP-0402')
                elif dq_dp_chain in [DQDPChain.ALPHA_DP, DQDPChain.ALPHA_DQ]:
                    hla_number = antibody.code.broad[2:]
                    if len(hla_number) == 1:
                        add_antibody(dq_dp_chain + '-0' + hla_number)
                    elif len(hla_number) == 2:
                        add_antibody(dq_dp_chain + '-' + hla_number)
                    else:
                        raise AssertionError
                else:
                    # DQB
                    add_antibody(antibody.code.display_code)

                logger.debug(f'Parsed {antibody.raw_code} -> {unacceptable_antibodies[-2:]}')

    return unacceptable_antibodies


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
