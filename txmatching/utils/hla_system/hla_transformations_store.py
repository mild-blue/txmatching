import itertools
import logging
from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_dto import (
    HLAAntibodiesDTO, HLAAntibodyDTO)
from txmatching.data_transfer_objects.patients.patient_parameters_dto import (
    HLATypingDTO, HLATypingRawDTO)
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import (HLAAntibodyRawModel,
                                                    ParsingErrorModel)
from txmatching.patients.hla_model import HLAType
from txmatching.utils.hla_system.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_transformations import (
    parse_hla_raw_code_with_details, preprocess_hla_code_in)

logger = logging.getLogger(__name__)


def parse_hla_antibodies_raw_and_store_parsing_error_in_db(
        hla_antibodies_raw: List[HLAAntibodyRawModel]
) -> HLAAntibodiesDTO:
    # TODOO: refactor
    @dataclass
    class HLAAntibodyPreprocessedDTO:
        raw_code: str
        mfi: int
        cutoff: int

    hla_antibodies_preprocessed = [
        HLAAntibodyPreprocessedDTO(preprocessed_raw_code, hla_antibody_raw.mfi, hla_antibody_raw.cutoff)
        for hla_antibody_raw in hla_antibodies_raw
        for preprocessed_raw_code in preprocess_hla_code_in(hla_antibody_raw.raw_code)
    ]

    # TODOO: improvement: return the rest at least
    grouped_hla_antibodies = itertools.groupby(sorted(hla_antibodies_preprocessed, key=lambda x: x.raw_code),
                                               key=lambda x: x.raw_code)
    for hla_code_raw, antibody_group in grouped_hla_antibodies:
        cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group}
        if len(cutoffs) > 1:
            _store_parsing_error(hla_code_raw, HlaCodeProcessingResultDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY)
            hla_antibodies_preprocessed = []

    hla_antibodies_parsed = []
    for hla_antibody in hla_antibodies_preprocessed:
        code = parse_hla_raw_code_and_store_parsing_error_in_db(hla_antibody.raw_code)
        if code is not None:
            hla_antibodies_parsed.append(
                HLAAntibodyDTO(
                    raw_code=hla_antibody.raw_code,
                    code=code,
                    mfi=hla_antibody.mfi,
                    cutoff=hla_antibody.cutoff,
                )
            )

    return HLAAntibodiesDTO(
        hla_antibodies_list=hla_antibodies_parsed
    )


def parse_hla_typing_raw_and_store_parsing_error_in_db(hla_typing_raw: HLATypingRawDTO) -> HLATypingDTO:
    raw_codes_preprocessed = [
        raw_code_preprocessed
        for hla_type_raw in hla_typing_raw.hla_types_list
        for raw_code_preprocessed in preprocess_hla_code_in(hla_type_raw.raw_code)
    ]

    hla_types_parsed = []
    for raw_code in raw_codes_preprocessed:
        code = parse_hla_raw_code_and_store_parsing_error_in_db(raw_code)
        if code is not None:
            hla_types_parsed.append(
                HLAType(
                    raw_code=raw_code,
                    code=code
                )
            )

    return HLATypingDTO(
        hla_types_list=hla_types_parsed
    )


def parse_hla_raw_code_and_store_parsing_error_in_db(hla_raw_code: str) -> Optional[str]:
    """
    Method to store information about error during parsing HLA code.
    This method is partially redundant to parse_hla_raw_code so in case of update, update it too.
    It must be in separated file with little redundancy caused by cyclic import:
    txmatching.database.sql_alchemy_schema -> txmatching.patients.patient ->
    txmatching.patients.patient_parameters -> txmatching.utils.hla_system.hla_transformations
    :param hla_raw_code: HLA raw code
    :return:
    """
    # TODOO: update comment as soon as parse_hla_raw_code is removed
    parsing_result = parse_hla_raw_code_with_details(hla_raw_code)
    if not parsing_result.maybe_hla_code or \
            parsing_result.result_detail != HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED:
        _store_parsing_error(hla_raw_code, parsing_result.result_detail)
    return parsing_result.maybe_hla_code


def _store_parsing_error(
        hla_code: str,
        hla_code_processing_result_detail: HlaCodeProcessingResultDetail
):
    parsing_error = ParsingErrorModel(
        hla_code=hla_code,
        hla_code_processing_result_detail=hla_code_processing_result_detail
    )
    db.session.add(parsing_error)
    db.session.commit()
