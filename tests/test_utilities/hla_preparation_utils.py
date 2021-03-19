from typing import List

from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingRawDTO
from txmatching.database.sql_alchemy_schema import HLAAntibodyRawModel
from txmatching.patients.hla_model import (HLAAntibodies, HLAAntibody,
                                           HLAAntibodyRaw, HLAType, HLATypeRaw,
                                           HLATyping)
from txmatching.utils.hla_system.hla_transformations_store import (
    parse_hla_antibodies_raw_and_add_parsing_error_to_db_session,
    parse_hla_raw_code_and_add_parsing_error_to_db_session,
    parse_hla_typing_raw_and_add_parsing_error_to_db_session)


def create_hla_typing(hla_types_list: List[str]) -> HLATyping:
    raw_type_list = [HLATypeRaw(hla_type) for hla_type in hla_types_list]
    typing_dto = HLATypingRawDTO(
        hla_types_list=raw_type_list
    )
    parsed_typing_dto = parse_hla_typing_raw_and_add_parsing_error_to_db_session(hla_typing_raw=typing_dto)
    return HLATyping(
        hla_types_raw_list=raw_type_list,
        hla_per_groups=parsed_typing_dto.hla_per_groups
    )


def create_hla_type(raw_code: str) -> HLAType:
    code = parse_hla_raw_code_and_add_parsing_error_to_db_session(raw_code)
    return HLAType(
        raw_code=raw_code,
        code=code
    )


# here we redundantly require too specific object, but its easiest, so we can reuse the parse function.
def create_antibodies(hla_antibodies_list: List[HLAAntibody]) -> HLAAntibodies:
    raw_antibodies_model = [HLAAntibodyRawModel(
        raw_code=hla_antibody.raw_code,
        mfi=hla_antibody.mfi,
        cutoff=hla_antibody.cutoff) for hla_antibody in hla_antibodies_list]
    raw_antibodies = [HLAAntibodyRaw(
        raw_code=hla_antibody.raw_code,
        mfi=hla_antibody.mfi,
        cutoff=hla_antibody.cutoff) for hla_antibody in hla_antibodies_list]
    dto = parse_hla_antibodies_raw_and_add_parsing_error_to_db_session(raw_antibodies_model)

    return HLAAntibodies(
        hla_antibodies_raw_list=raw_antibodies,
        hla_antibodies_per_groups=dto.hla_antibodies_per_groups
    )


def create_antibody(raw_code, mfi, cutoff) -> HLAAntibody:
    hla_antibody = parse_hla_raw_code_and_add_parsing_error_to_db_session(raw_code)
    return HLAAntibody(
        raw_code=raw_code,
        code=hla_antibody,
        mfi=mfi,
        cutoff=cutoff,
    )