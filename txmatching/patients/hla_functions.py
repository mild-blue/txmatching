import itertools
import logging
import re
from collections import namedtuple
from typing import Dict, List, Tuple, Union

from txmatching.data_transfer_objects.hla.parsing_issue_dto import \
    ParsingIssueBase
from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibody,
                                           HLAPerGroup, HLAType)
from txmatching.utils.constants import \
    SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES
from txmatching.utils.enums import (GENE_HLA_GROUPS_WITH_OTHER,
                                    HLA_GROUPS_OTHER, HLA_GROUPS_PROPERTIES,
                                    HLAGroup)
from txmatching.utils.hla_system.hla_transformations.get_mfi_from_multiple_hla_codes import \
    get_mfi_from_multiple_hla_codes
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.utils.hla_system.rel_dna_ser_exceptions import \
    MULTIPLE_SERO_CODES_LIST

logger = logging.getLogger(__name__)


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
        match_found = False
        for hla_group in HLA_GROUPS_OTHER:
            if _is_hla_type_in_group(hla_type, hla_group):
                hla_types_in_groups[hla_group] += [hla_type]
                match_found = True
                break
        if not match_found:
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=hla_type.raw_code,
                    parsing_issue_detail=ParsingIssueDetail.OTHER_PROBLEM,
                    message=f'HLA type or hla antibody was parsed as {hla_type} but do not belong to any OTHER group. '
                            f'This should never happen. This unexpected HLA will be ignored.'
                )
            )
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
    def _group_key(hla_antibody: HLAAntibody) -> str:
        return hla_antibody.raw_code

    parsing_issues = []
    grouped_hla_antibodies = itertools.groupby(sorted(hla_antibodies, key=_group_key),
                                               key=_group_key)
    hla_antibodies_joined = []
    for hla_code_raw, antibody_group in grouped_hla_antibodies:
        antibody_group_list = list(antibody_group)
        assert len(antibody_group_list) > 0
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
        mfi_parsing_issues, mfi = get_mfi_from_multiple_hla_codes([hla_code.mfi for hla_code in antibody_group_list],
                                                                  cutoff,
                                                                  hla_code_raw)
        parsing_issues = parsing_issues + mfi_parsing_issues
        new_antibody = HLAAntibody(
            code=antibody_group_list[0].code,
            raw_code=hla_code_raw,
            cutoff=cutoff,
            mfi=mfi
        )
        hla_antibodies_joined.append(new_antibody)

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
    for hla_group in GENE_HLA_GROUPS_WITH_OTHER:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_types:
        match_found = False
        for hla_group in GENE_HLA_GROUPS_WITH_OTHER:
            if _is_hla_type_in_group(hla_type, hla_group):
                hla_types_in_groups[hla_group].append(hla_type)
                match_found = True
                break
        if not match_found:
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=hla_type.raw_code,
                    parsing_issue_detail=ParsingIssueDetail.OTHER_PROBLEM,
                    message=f'HLA type or hla antibody was parsed as {hla_type} but do not belong to any group. '
                            f'This should never happen. This unexpected HLA will be ignored.',
                )
            )
    return parsing_issues, hla_types_in_groups


def is_all_antibodies_in_high_res(recipient_antibodies: List[HLAAntibody]) -> bool:
    for antibody in recipient_antibodies:
        # TODO the not in multiple sero codes list is ugly hack, improve in
        #  https://github.com/mild-blue/txmatching/issues/1036
        if antibody.code.high_res is None and antibody.code.split not in MULTIPLE_SERO_CODES_LIST:
            return False
    return True


def parse_if_high_res_antibodies_in_sufficient_amount_and_some_below_cutoff(
        recipient_antibodies: List[HLAAntibody]) -> Tuple[bool, ParsingIssueDetail]:
    assert is_all_antibodies_in_high_res(recipient_antibodies), \
        'This method is available just for antibodies in high res.'

    is_some_antibody_below_cutoff = False
    for antibody in recipient_antibodies:
        if antibody.mfi < antibody.cutoff:
            is_some_antibody_below_cutoff = True

    BoolParsingIssueNamedtuple = namedtuple('BoolParsingIssue', ['bool', 'parsing_issue'])

    if not is_some_antibody_below_cutoff:
        return BoolParsingIssueNamedtuple(False,
                                          ParsingIssueDetail.ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES)
    elif is_some_antibody_below_cutoff and len(recipient_antibodies) < SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES:
        return BoolParsingIssueNamedtuple(False,
                                          ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES)
    return BoolParsingIssueNamedtuple(True,
                                      ParsingIssueDetail.SUCCESSFULLY_PARSED)
