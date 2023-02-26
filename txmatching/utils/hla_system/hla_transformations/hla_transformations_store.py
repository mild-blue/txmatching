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
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLAAntibodyRaw
from txmatching.patients.hla_functions import (
    analyze_if_high_res_antibodies_are_type_a,
    create_hla_antibodies_per_groups_from_hla_antibodies,
    is_all_antibodies_in_high_res, split_hla_types_to_groups)
from txmatching.patients.hla_model import HLAAntibody, HLAPerGroup, HLAType
from txmatching.utils.enums import GENE_HLA_GROUPS, HLA_GROUPS_PROPERTIES, HLAGroup
from txmatching.utils.hla_system.hla_transformations.hla_transformations import (
    parse_hla_raw_code_with_details, preprocess_hla_code_in)
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import (
    OK_PROCESSING_RESULTS, ParsingIssueDetail)

logger = logging.getLogger(__name__)

MAX_ANTIGENS_PER_GROUP = 2
MAX_ANTIGENS_PER_OTHER_DR = 3


def parse_hla_raw_code_and_return_parsing_issue_list(
        hla_raw_code: str
) -> Tuple[List[ParsingIssueBase], Optional[HLACode]]:
    """
    Method to store information about issues during parsing HLA code.
    :param hla_raw_code: HLA raw code
    :return:
    """
    parsing_issues = []
    processing_result = parse_hla_raw_code_with_details(hla_raw_code)
    if not processing_result.maybe_hla_code or processing_result.result_detail not in OK_PROCESSING_RESULTS:
        parsing_issues.append(
            ParsingIssueBase(
                hla_code_or_group=hla_raw_code,
                parsing_issue_detail=processing_result.result_detail,
                message=processing_result.result_detail.value,
            )
        )
    return parsing_issues, processing_result.maybe_hla_code


# pylint: disable=too-many-locals
def parse_hla_antibodies_raw_and_return_parsing_issue_list(
        hla_antibodies_raw: List[HLAAntibodyRaw]
) -> Tuple[List[ParsingIssueBase], HLAAntibodiesDTO]:
    # 1. preprocess raw codes (their count can increase)
    @dataclass
    class HLAAntibodyPreprocessedDTO:
        raw_code: str
        mfi: int
        cutoff: int
        secondary_raw_code: Optional[str] = None

    parsing_issues = []

    hla_antibodies_preprocessed = [
        HLAAntibodyPreprocessedDTO(preprocessed_antibody.raw_code, hla_antibody_raw.mfi,
                                   hla_antibody_raw.cutoff, preprocessed_antibody.secondary_raw_code)
        for hla_antibody_raw in hla_antibodies_raw
        for preprocessed_antibody in preprocess_hla_code_in(hla_antibody_raw.raw_code)
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
            hla_antibodies_parsed.append(
                HLAAntibody(
                    raw_code=hla_antibody.raw_code,
                    code=code,
                    mfi=hla_antibody.mfi,
                    cutoff=hla_antibody.cutoff
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
        preprocessed_antigen.raw_code
        for hla_type_raw in hla_typing_raw.hla_types_list
        for preprocessed_antigen in preprocess_hla_code_in(hla_type_raw.raw_code)
    ]

    # 2. parse preprocessed codes and keep only valid ones
    hla_types_parsed = []
    for raw_code in raw_codes_preprocessed:
        raw_codes_parsing_issues, code = parse_hla_raw_code_and_return_parsing_issue_list(raw_code)
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

    # 4. check if the number of hla_types per group exceedes the max number of hla_types for that group
    for group in hla_per_groups:
        if group_exceedes_max_number_of_hla_types(group.hla_types, group.hla_group):
            invalid_hla_groups.append(group.hla_group.name)
            group_name = 'Group ' + group.hla_group.name
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
        if group.hla_group in GENE_HLA_GROUPS and basic_group_is_empty(group.hla_types):
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


def group_exceedes_max_number_of_hla_types(hla_types: List[HLAType], hla_group: HLAGroup):
    if hla_group is not HLAGroup.INVALID_CODES and len(hla_types) > HLA_GROUPS_PROPERTIES[hla_group].max_count_per_patient:
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

    maybe_parsing_issue = analyze_if_high_res_antibodies_are_type_a(
        recipient_antibodies).maybe_parsing_issue
    if maybe_parsing_issue is not None:
        return ParsingIssueBase(hla_code_or_group='Antibodies',
                                parsing_issue_detail=maybe_parsing_issue,
                                message=maybe_parsing_issue.value)
    return None
