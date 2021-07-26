import itertools
import logging
import re
from typing import Dict, List, Union

from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibody,
                                           HLAPerGroup, HLAType)
from txmatching.utils.enums import (GENE_HLA_GROUPS_WITH_OTHER,
                                    HLA_GROUPS_PROPERTIES, HLAGroup, HLA_GROUPS_OTHER)
from txmatching.utils.hla_system.hla_transformations.get_mfi_from_multiple_hla_codes import \
    get_mfi_from_multiple_hla_codes
from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_transformations.parsing_error import (
    ParsingInfo, add_parsing_error_to_db_session)

logger = logging.getLogger(__name__)


def split_hla_types_to_groups(hla_types: List[HLAType], parsing_info: ParsingInfo = None) -> List[HLAPerGroup]:
    hla_types_in_groups = _split_hla_types_to_groups(hla_types, parsing_info)
    return [HLAPerGroup(hla_group,
                        sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                        ) for hla_group, hla_codes_in_group in
            hla_types_in_groups.items()]


def split_hla_types_to_groups_other(
        hla_types: List[HLAType],
        parsing_info: ParsingInfo = None
) -> Dict[HLAGroup, List[HLAType]]:
    hla_types_in_groups = dict()
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
            add_parsing_error_to_db_session(
                hla_type.raw_code, HlaCodeProcessingResultDetail.OTHER_PROBLEM,
                f'HLA type or hla antibody was parsed as {hla_type} but do not belong to any group. '
                f'This should never happen. This unexpected HLA will be ignored.',
                parsing_info
            )
    return hla_types_in_groups


def create_hla_antibodies_per_groups_from_hla_antibodies(
        hla_antibodies: List[HLAAntibody],
        parsing_info: ParsingInfo = None
) -> List[AntibodiesPerGroup]:
    hla_antibodies_joined = _join_duplicate_antibodies(hla_antibodies, parsing_info)
    hla_antibodies_per_groups = _split_antibodies_to_groups(hla_antibodies_joined, parsing_info)
    return hla_antibodies_per_groups


def _split_antibodies_to_groups(hla_antibodies: List[HLAAntibody],
                                parsing_info: ParsingInfo = None) -> List[AntibodiesPerGroup]:
    hla_antibodies_in_groups = _split_hla_types_to_groups(hla_antibodies, parsing_info)
    return [AntibodiesPerGroup(hla_group,
                               sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                               ) for hla_group, hla_codes_in_group in
            hla_antibodies_in_groups.items()]


def _join_duplicate_antibodies(
        hla_antibodies: List[HLAAntibody],
        parsing_info: ParsingInfo = None
) -> List[HLAAntibody]:
    def _group_key(hla_antibody: HLAAntibody) -> str:
        return hla_antibody.raw_code

    grouped_hla_antibodies = itertools.groupby(sorted(hla_antibodies, key=_group_key),
                                               key=_group_key)
    hla_antibodies_joined = []
    for hla_code_raw, antibody_group in grouped_hla_antibodies:
        antibody_group_list = list(antibody_group)
        assert len(antibody_group_list) > 0
        cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group_list}
        if len(cutoffs) != 1:
            add_parsing_error_to_db_session(
                hla_code_raw,
                HlaCodeProcessingResultDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY,
                message=HlaCodeProcessingResultDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY.value,
                parsing_info=parsing_info
            )
            continue

        cutoff = cutoffs.pop()
        mfi = get_mfi_from_multiple_hla_codes([hla_code.mfi for hla_code in antibody_group_list],
                                              cutoff,
                                              hla_code_raw,
                                              parsing_info)
        new_antibody = HLAAntibody(
            code=antibody_group_list[0].code,
            raw_code=hla_code_raw,
            cutoff=cutoff,
            mfi=mfi
        )
        hla_antibodies_joined.append(new_antibody)

    return hla_antibodies_joined


HLACodeAlias = Union[HLAType, HLAAntibody]


def _is_hla_type_in_group(hla_type: HLACodeAlias, hla_group: HLAGroup) -> bool:
    if hla_type.code.broad is not None:
        return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].split_code_regex, hla_type.code.broad))
    elif hla_type.code.high_res is not None:
        return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex, hla_type.code.high_res))
    else:
        raise AssertionError(f'Broad or high res should be provided: {hla_type.code}')


def _split_hla_types_to_groups(hla_types: List[HLACodeAlias],
                               parsing_info: ParsingInfo
                               ) -> Dict[HLAGroup, List[HLACodeAlias]]:
    hla_types_in_groups = dict()
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
            add_parsing_error_to_db_session(
                hla_type.raw_code, HlaCodeProcessingResultDetail.OTHER_PROBLEM,
                f'HLA type or hla antibody was parsed as {hla_type} but do not belong to any group. '
                f'This should never happen. This unexpected HLA will be ignored.',
                parsing_info
            )
    return hla_types_in_groups
