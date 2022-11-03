import itertools
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

from txmatching.data_transfer_objects.hla.parsing_issue_dto import \
    ParsingIssueBase
from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesDTO
from txmatching.data_transfer_objects.patients.patient_parameters_dto import (
    HLATypingDTO, HLATypingRawDTO)
from txmatching.database.sql_alchemy_schema import HLAAntibodyRawModel
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_functions import (
    create_hla_antibodies_per_groups_from_hla_antibodies,
    is_all_antibodies_in_high_res,
    is_high_res_antibodies_in_sufficient_amount_and_not_all_above_cutoff,
    split_hla_types_to_groups, split_hla_types_to_groups_other)
from txmatching.patients.hla_model import HLAAntibody, HLAPerGroup, HLAType
from txmatching.utils.enums import HLA_GROUPS_OTHER, HLAGroup
from txmatching.utils.hla_system.hla_transformations.hla_transformations import (
    parse_hla_raw_code_with_details, preprocess_hla_code_in)
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import (
    OK_PROCESSING_RESULTS, ParsingIssueDetail)

logger = logging.getLogger(__name__)

MAX_ANTIGENS_PER_GROUP = 2


def parse_hla_raw_code_and_return_parsing_issue_list(
        hla_raw_code: str
) -> Tuple[List[ParsingIssueBase], Optional[HLACode]]:
    """
    Method to store information about issues during parsing HLA code.
    This method is partially redundant to parse_hla_raw_code so in case of update, update it too.
    It must be in separated file with little redundancy caused by cyclic import:
    txmatching.database.sql_alchemy_schema -> txmatching.patients.patient ->
    txmatching.patients.patient_parameters -> txmatching.utils.hla_system.hla_transformations
    :param hla_raw_code: HLA raw code
    :return:
    """
    parsing_issues = []
    parsing_issue = parse_hla_raw_code_with_details(hla_raw_code)
    if not parsing_issue.maybe_hla_code or parsing_issue.result_detail not in OK_PROCESSING_RESULTS:
        parsing_issues.append(
            ParsingIssueBase(
                hla_code_or_group=hla_raw_code,
                parsing_issue_detail=parsing_issue.result_detail,
                message=parsing_issue.result_detail.value,
            )
        )
    return parsing_issues, parsing_issue.maybe_hla_code


# pylint: disable=too-many-locals
def parse_hla_antibodies_raw_and_return_parsing_issue_list(
        hla_antibodies_raw: List[HLAAntibodyRawModel]
) -> Tuple[List[ParsingIssueBase], HLAAntibodiesDTO]:
    # 1. preprocess raw codes (their count can increase)
    @dataclass
    class HLAAntibodyPreprocessedDTO:
        raw_code: str
        mfi: int
        cutoff: int

    parsing_issues = []

    hla_antibodies_preprocessed = [
        HLAAntibodyPreprocessedDTO(preprocessed_raw_code, hla_antibody_raw.mfi, hla_antibody_raw.cutoff)
        for hla_antibody_raw in hla_antibodies_raw
        for preprocessed_raw_code in preprocess_hla_code_in(hla_antibody_raw.raw_code)
    ]

    # 2. parse preprocessed codes and keep only valid ones
    grouped_hla_antibodies = itertools.groupby(
        sorted(hla_antibodies_preprocessed, key=lambda x: x.raw_code),
        key=lambda x: x.raw_code
    )
    hla_antibodies_parsed = []
    for raw_code, antibody_group_generator in grouped_hla_antibodies:
        antibody_group = list(antibody_group_generator)
        # Antibodies with the same raw code does need to have the same cutoff
        cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group}
        if len(cutoffs) > 1:
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=raw_code,
                    parsing_issue_detail=ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY,
                    message=ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY.value,
                )
            )
            continue

        # Parse antibodies and keep only valid ones
        for hla_antibody in antibody_group:
            antibody_parsing_issues, code = parse_hla_raw_code_and_return_parsing_issue_list(hla_antibody.raw_code)
            if code is not None:
                hla_antibodies_parsed.append(
                    HLAAntibody(
                        raw_code=hla_antibody.raw_code,
                        code=code,
                        mfi=hla_antibody.mfi,
                        cutoff=hla_antibody.cutoff,
                    )
                )
            parsing_issues = parsing_issues + antibody_parsing_issues

    # 3. validate antibodies
    parsing_issue = _get_parsing_issue_for_almost_valid_antibodies(hla_antibodies_parsed)
    if parsing_issue is not None:
        parsing_issues.append(parsing_issue)

    # 4. split antibodies to groups (and join duplicates)
    antibodies_per_groups_parsing_issues, hla_antibodies_per_groups = create_hla_antibodies_per_groups_from_hla_antibodies(
        hla_antibodies_parsed
    )

    parsing_issues = parsing_issues + antibodies_per_groups_parsing_issues

    return (parsing_issues, HLAAntibodiesDTO(
        hla_antibodies_per_groups=hla_antibodies_per_groups
    ))


def parse_hla_typing_raw_and_return_parsing_issue_list(
        hla_typing_raw: HLATypingRawDTO,
) -> Tuple[List[ParsingIssueBase], HLATypingDTO]:
    parsing_issues = []
    # 1. preprocess raw codes (their count can increase)
    raw_codes_preprocessed = [
        raw_code_preprocessed
        for hla_type_raw in hla_typing_raw.hla_types_list
        for raw_code_preprocessed in preprocess_hla_code_in(hla_type_raw.raw_code)
    ]

    # 2. parse preprocessed codes and keep only valid ones
    hla_types_parsed = []
    for raw_code in raw_codes_preprocessed:
        raw_codes_parsing_issues, code = parse_hla_raw_code_and_return_parsing_issue_list(raw_code)
        if code is not None:
            hla_types_parsed.append(
                HLAType(
                    raw_code=raw_code,
                    code=code
                )
            )
        parsing_issues = parsing_issues + raw_codes_parsing_issues

    # 3. split hla_types_parsed to the groups
    hla_per_groups_parsing_issues, hla_per_groups = split_hla_types_to_groups(hla_types_parsed)

    parsing_issues = parsing_issues + hla_per_groups_parsing_issues

    invalid_hla_groups = []

    # 4. check if there are max 2 hla_types per group
    for group in hla_per_groups:
        if group.hla_group != HLAGroup.Other and group_exceedes_max_number_of_hla_types(group.hla_types):
            invalid_hla_groups.append(group.hla_group.name)
            group_name = 'Group ' + group.hla_group.name
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=group_name,
                    parsing_issue_detail=ParsingIssueDetail.MORE_THAN_TWO_HLA_CODES_PER_GROUP,
                    message=ParsingIssueDetail.MORE_THAN_TWO_HLA_CODES_PER_GROUP.value
                )
            )
        if group.hla_group == HLAGroup.Other:
            codes_per_group_parsing_issues, hla_codes_per_group_other = split_hla_types_to_groups_other(group.hla_types)
            parsing_issues = parsing_issues + codes_per_group_parsing_issues
            for hla_group in HLA_GROUPS_OTHER:
                if group_exceedes_max_number_of_hla_types(hla_codes_per_group_other[hla_group]):
                    invalid_hla_groups.append(hla_group.name)
                    group_name = 'Group ' + hla_group.name
                    parsing_issues.append(
                        ParsingIssueBase(
                            hla_code_or_group=group_name,
                            parsing_issue_detail=ParsingIssueDetail.MORE_THAN_TWO_HLA_CODES_PER_GROUP,
                            message=ParsingIssueDetail.MORE_THAN_TWO_HLA_CODES_PER_GROUP.value
                        )
                    )

    # TODO https://github.com/mild-blue/txmatching/issues/790 hla_code should be nullable
    # 5. check if a basic group is missing
    for group in hla_per_groups:
        if group.hla_group != HLAGroup.Other and basic_group_is_empty(group.hla_types):
            invalid_hla_groups.append(group.hla_group.name)
            group_name = 'Group ' + group.hla_group.name
            parsing_issues.append(
                ParsingIssueBase(
                    hla_code_or_group=group_name,
                    parsing_issue_detail=ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
                    message=ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY.value
                )
            )

    return (parsing_issues, HLATypingDTO(
        hla_per_groups=[
            HLAPerGroup(
                hla_group=group.hla_group,
                hla_types=[hla_type for hla_type in group.hla_types if group.hla_group.name not in invalid_hla_groups]
            ) for group in hla_per_groups
        ],
    ))


def group_exceedes_max_number_of_hla_types(hla_types: List[HLAType]):
    if len(hla_types) > MAX_ANTIGENS_PER_GROUP:
        return True
    return False


def basic_group_is_empty(hla_types: List[HLAType]):
    if len(hla_types) == 0:
        return True
    return False


def _get_parsing_issue_for_almost_valid_antibodies(recipient_antibodies: List[HLAAntibody]) \
        -> Optional[ParsingIssueBase]:
    if len(recipient_antibodies) == 0:
        return None
    if not is_all_antibodies_in_high_res(recipient_antibodies):
        return None

    _, parse_detail = \
        is_high_res_antibodies_in_sufficient_amount_and_not_all_above_cutoff(recipient_antibodies)
    if parse_detail != ParsingIssueDetail.SUCCESSFULLY_PARSED:
        return ParsingIssueBase(hla_code_or_group='Antibodies',
                                parsing_issue_detail=parse_detail,
                                message=parse_detail.value)
    return None
