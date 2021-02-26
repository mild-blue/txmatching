import itertools
import logging
from dataclasses import dataclass
from typing import List, Optional, Union

from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesDTO
from txmatching.data_transfer_objects.patients.patient_parameters_dto import (
    HLATypingDTO, HLATypingRawDTO)
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import (HLAAntibodyRawModel,
                                                    ParsingErrorModel)
from txmatching.patients.hla_model import (
    HLAAntibody, HLAType, create_hla_antibodies_per_groups_from_hla_antibodies,
    split_hla_types_to_groups)
from txmatching.utils.hla_system.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_transformations import (
    parse_hla_raw_code_with_details, preprocess_hla_code_in)
from txmatching.utils.logging_tools import PatientAdapter

logger = logging.getLogger(__name__)


def parse_hla_antibodies_raw_and_store_parsing_error_in_db(
        hla_antibodies_raw: List[HLAAntibodyRawModel],
        # TODO: https://github.com/mild-blue/txmatching/issues/496 replace logging with storing in db along
        #  with patient medical id. Change it also in other places.
        logger_with_patient: Union[logging.Logger, PatientAdapter] = logging.getLogger(__name__)
) -> HLAAntibodiesDTO:
    # 1. preprocess raw codes (their count can increase)
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

    # 2. parse preprocessed codes and keep only valid ones
    grouped_hla_antibodies = itertools.groupby(
        sorted(hla_antibodies_preprocessed, key=lambda x: x.raw_code),
        key=lambda x: x.raw_code
    )
    hla_antibodies_parsed = []
    for raw_code, antibody_group in grouped_hla_antibodies:
        # Antibodies with the same raw code does need to have the same cutoff
        cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group}
        if len(cutoffs) > 1:
            _store_parsing_error(raw_code, HlaCodeProcessingResultDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY)
            continue

        # Parse antibodies and keep only valid ones
        for hla_antibody in antibody_group:
            code = parse_hla_raw_code_and_store_parsing_error_in_db(hla_antibody.raw_code)
            if code is not None:
                hla_antibodies_parsed.append(
                    HLAAntibody(
                        raw_code=hla_antibody.raw_code,
                        code=code,
                        mfi=hla_antibody.mfi,
                        cutoff=hla_antibody.cutoff,
                    )
                )

    # 3. filter antibodies over cutoff and split to groups
    hla_antibodies_per_groups = create_hla_antibodies_per_groups_from_hla_antibodies(hla_antibodies_parsed, logger_with_patient)

    return HLAAntibodiesDTO(
        hla_antibodies_list=hla_antibodies_parsed,
        hla_antibodies_per_groups=hla_antibodies_per_groups
    )


def parse_hla_typing_raw_and_store_parsing_error_in_db(hla_typing_raw: HLATypingRawDTO) -> HLATypingDTO:
    # 1. preprocess raw codes (their count can increase)
    raw_codes_preprocessed = [
        raw_code_preprocessed
        for hla_type_raw in hla_typing_raw.hla_types_list
        for raw_code_preprocessed in preprocess_hla_code_in(hla_type_raw.raw_code)
    ]

    # 2. parse preprocessed codes and keep only valid ones
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

    # 3. split hla_types_parsed to the groups
    hla_per_groups = split_hla_types_to_groups(hla_types_parsed)

    return HLATypingDTO(
        hla_types_list=hla_types_parsed,
        hla_per_groups=hla_per_groups,
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
