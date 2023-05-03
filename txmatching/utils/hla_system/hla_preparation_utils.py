from typing import List

from txmatching.data_transfer_objects.patients.patient_parameters_dto import HLATypingRawDTO
from txmatching.patients.hla_model import HLATyping, HLATypeRaw, HLAType, HLAAntibodyRaw, \
    HLAAntibodies, HLAAntibody
from txmatching.utils.enums import HLAAntibodyType
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import \
    parse_hla_typing_raw_and_return_parsing_issue_list, \
    parse_hla_raw_code_and_return_parsing_issue_list, \
    parse_hla_antibodies_raw_and_return_parsing_issue_list


def create_hla_typing(hla_types_list: List[str],
                      ignore_max_number_hla_types_per_group: bool = False) -> HLATyping:
    raw_type_list = [HLATypeRaw(hla_type) for hla_type in hla_types_list]
    typing_dto = HLATypingRawDTO(
        hla_types_list=raw_type_list
    )
    parsed_typing_dto = parse_hla_typing_raw_and_return_parsing_issue_list(
        hla_typing_raw=typing_dto,
        ignore_max_number_hla_types=ignore_max_number_hla_types_per_group)[1]
    return HLATyping(
        hla_types_raw_list=raw_type_list,
        hla_per_groups=parsed_typing_dto.hla_per_groups
    )


def create_hla_type(raw_code: str) -> HLAType:
    code = parse_hla_raw_code_and_return_parsing_issue_list(raw_code)[1]
    return HLAType(
        raw_code=raw_code,
        code=code
    )


# here we redundantly require too specific object, but its easiest, so we can reuse the parse function.
def create_antibodies(hla_antibodies_list: List[HLAAntibodyRaw]) -> HLAAntibodies:
    dto = parse_hla_antibodies_raw_and_return_parsing_issue_list(hla_antibodies_list)[1]

    return HLAAntibodies(
        hla_antibodies_raw_list=hla_antibodies_list,
        hla_antibodies_per_groups=dto.hla_antibodies_per_groups
    )


def create_antibody(raw_code: str, mfi: int, cutoff: int) -> HLAAntibodyRaw:
    return HLAAntibodyRaw(
        raw_code=raw_code,
        mfi=mfi,
        cutoff=cutoff
    )


def create_antibody_parsed(raw_code: str, mfi: int, cutoff: int, second_raw_code: str = None,
                           antibody_type: HLAAntibodyType = HLAAntibodyType.NORMAL) -> HLAAntibody:
    code = parse_hla_raw_code_and_return_parsing_issue_list(raw_code)[1]
    second_code = parse_hla_raw_code_and_return_parsing_issue_list(
        second_raw_code)[1] if second_raw_code is not None else None
    return HLAAntibody(
        raw_code=raw_code,
        code=code,
        mfi=mfi,
        cutoff=cutoff,
        second_raw_code=second_raw_code,
        second_code=second_code,
        type=antibody_type
    )
