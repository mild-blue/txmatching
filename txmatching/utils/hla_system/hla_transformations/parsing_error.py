from dataclasses import dataclass
from typing import List

from sqlalchemy import and_

from txmatching.data_transfer_objects.hla.parsing_error_dto import ParsingError
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import ParsingErrorModel
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail


@dataclass
class ParsingInfo:
    txm_event_id: int
    donor_id: int = None
    recipient_id: int = None


# You need to commit the session to save the changes to the db (db.session.commit())
def add_parsing_error_to_db_session(
        hla_code_or_group: str,
        parsing_issue_detail: ParsingIssueDetail,
        message: str,
        parsing_info: ParsingInfo = None
):
    parsing_error = ParsingErrorModel(
        hla_code_or_group=hla_code_or_group,
        parsing_issue_detail=parsing_issue_detail,
        message=message,
        donor_id = parsing_info.donor_id,
        recipient_id = parsing_info.recipient_id,
        txm_event_id=parsing_info.txm_event_id if parsing_info is not None else None,
    )
    db.session.add(parsing_error)


def _convert_parsing_error_models_to_dataclasses(parsing_error_models: List[ParsingErrorModel]) -> List[ParsingError]:
    return [ParsingError(
        hla_code_or_group=parsing_error_model.hla_code_or_group,
        parsing_issue_detail=parsing_error_model.parsing_issue_detail.name,
        message=parsing_error_model.message,
        donor_id = parsing_error_model.donor_id,
        recipient_id = parsing_error_model.recipient_id,
        txm_event_id=parsing_error_model.txm_event_id
    ) for parsing_error_model in parsing_error_models
        # TODO: https://github.com/mild-blue/txmatching/issues/629
        if parsing_error_model.parsing_issue_detail != ParsingIssueDetail.MFI_PROBLEM]


def get_parsing_errors_for_txm_event_id(txm_event_id: int) -> List[ParsingError]:
    return _convert_parsing_error_models_to_dataclasses(
        ParsingErrorModel.query.filter(
            ParsingErrorModel.txm_event_id == txm_event_id
        ).all()
    )


def get_parsing_errors_for_patients(txm_event_id: int, donor_ids: List[int] = [], recipient_ids: List[int] = []) -> List[ParsingError]:
    parsing_errors = ParsingErrorModel.query.filter(
        and_(ParsingErrorModel.donor_id.in_(donor_ids),
                ParsingErrorModel.txm_event_id == txm_event_id)
    ).all() + ParsingErrorModel.query.filter(
        and_(ParsingErrorModel.recipient_id.in_(recipient_ids),
                ParsingErrorModel.txm_event_id == txm_event_id)
    ).all()

    return _convert_parsing_error_models_to_dataclasses(parsing_errors)


def delete_parsing_errors_for_patient(
        txm_event_id: int,
        donor_id: int = None,
        recipient_id: int = None,
):
    if recipient_id is not None:
        ParsingErrorModel.query.filter(
            and_(ParsingErrorModel.recipient_id == recipient_id,
                ParsingErrorModel.txm_event_id == txm_event_id)
        ).delete()
    else:
        ParsingErrorModel.query.filter(
            and_(ParsingErrorModel.donor_id == donor_id,
                ParsingErrorModel.txm_event_id == txm_event_id)
        ).delete()


def delete_parsing_errors_for_txm_event_id(txm_event_id: int):
    ParsingErrorModel.query.filter(
        ParsingErrorModel.txm_event_id == txm_event_id
    ).delete()
