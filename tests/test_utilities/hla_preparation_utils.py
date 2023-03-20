from typing import List

from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingRawDTO
from txmatching.database.sql_alchemy_schema import HLAAntibodyRawModel
from txmatching.patients.hla_model import (HLAAntibodies, HLAAntibody,
                                           HLAAntibodyRaw, HLAType, HLATypeRaw,
                                           HLATyping)
from txmatching.utils.enums import HLAAntibodyType
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import (
    parse_hla_antibodies_raw_and_return_parsing_issue_list,
    parse_hla_raw_code_and_return_parsing_issue_list,
    parse_hla_typing_raw_and_return_parsing_issue_list)


def create_hla_typing(hla_types_list: List[str]) -> HLATyping:
    raw_type_list = [HLATypeRaw(hla_type) for hla_type in hla_types_list]
    typing_dto = HLATypingRawDTO(
        hla_types_list=raw_type_list
    )
    parsed_typing_dto = parse_hla_typing_raw_and_return_parsing_issue_list(hla_typing_raw=typing_dto)[1]
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
def create_antibodies(hla_antibodies_list: List[HLAAntibody]) -> HLAAntibodies:
    raw_antibodies_model = [HLAAntibodyRawModel(
        raw_code=hla_antibody.raw_code if hla_antibody.second_raw_code is None else _create_raw_code_for_double_antibody(
            hla_antibody),
        mfi=hla_antibody.mfi,
        cutoff=hla_antibody.cutoff) for hla_antibody in hla_antibodies_list]
    raw_antibodies = [HLAAntibodyRaw(
        raw_code=hla_antibody.raw_code if hla_antibody.second_raw_code is None else _create_raw_code_for_double_antibody(
            hla_antibody),
        mfi=hla_antibody.mfi,
        cutoff=hla_antibody.cutoff) for hla_antibody in hla_antibodies_list]
    dto = parse_hla_antibodies_raw_and_return_parsing_issue_list(raw_antibodies_model)[1]

    return HLAAntibodies(
        hla_antibodies_raw_list=raw_antibodies,
        hla_antibodies_per_groups=dto.hla_antibodies_per_groups
    )


def _create_raw_code_for_double_antibody(hla_antibody: HLAAntibody) -> str:
    return hla_antibody.raw_code[:2] + "[" + hla_antibody.raw_code.split("*")[1] + "," + hla_antibody.second_raw_code.split("*")[1] + "]"


def create_antibody(raw_code: str, mfi: int, cutoff: int, second_raw_code: str = None,
                    antibody_type: HLAAntibodyType = HLAAntibodyType.NORMAL) -> HLAAntibody:
    code = parse_hla_raw_code_and_return_parsing_issue_list(raw_code)[1]
    second_code = parse_hla_raw_code_and_return_parsing_issue_list(second_raw_code)[1]
    return HLAAntibody(
        raw_code=raw_code,
        code=code,
        mfi=mfi,
        cutoff=cutoff,
        second_raw_code=second_raw_code,
        second_code=second_code,
        type=antibody_type
    )
