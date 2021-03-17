from typing import List

from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingRawDTO
from txmatching.patients.hla_model import HLAType, HLATypeRaw, HLATyping
from txmatching.utils.hla_system.hla_transformations_store import (
    parse_hla_raw_code_and_add_parsing_error_to_db_session,
    parse_hla_typing_raw_and_add_parsing_error_to_db_session)


def get_hla_typing(hla_types_list: List[str]) -> HLATyping:
    raw_type_list = [HLATypeRaw(hla_type) for hla_type in hla_types_list]
    typing_dto = HLATypingRawDTO(
        hla_types_list=raw_type_list
    )
    parsed_typing_dto = parse_hla_typing_raw_and_add_parsing_error_to_db_session(hla_typing_raw=typing_dto)
    return HLATyping(
        hla_types_raw_list=raw_type_list,
        hla_per_groups=parsed_typing_dto.hla_per_groups
    )


def get_hla_type(raw_code: str) -> HLAType:
    code = parse_hla_raw_code_and_add_parsing_error_to_db_session(raw_code)
    return HLAType(
        raw_code=raw_code,
        code=code
    )
