from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import ParsingErrorModel
from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail
from txmatching.utils.logging_tools import ParsingInfo


# You need to commit the session to save the changes to the db (db.session.commit())
def add_parsing_error_to_db_session(
        hla_code: str,
        hla_code_processing_result_detail: HlaCodeProcessingResultDetail,
        message: str,
        parsing_info: ParsingInfo = None
):
    parsing_error = ParsingErrorModel(
        hla_code=hla_code,
        hla_code_processing_result_detail=hla_code_processing_result_detail,
        message=message,
        medical_id=parsing_info.medical_id if parsing_info is not None else None
    )
    db.session.add(parsing_error)
