import logging
from typing import Optional

from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import ParsingError
from txmatching.utils.hla_system.hla_code_processing_result_detail import HlaCodeProcessingResultDetail
from txmatching.utils.hla_system.hla_transformations import parse_hla_raw_code_with_details

logger = logging.getLogger(__name__)


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
    parsing_error = ParsingError(
        hla_code=hla_code,
        hla_code_processing_result_detail=hla_code_processing_result_detail
    )
    db.session.add(parsing_error)
    db.session.commit()
