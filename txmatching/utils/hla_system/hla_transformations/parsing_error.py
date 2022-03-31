from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import and_

from txmatching.data_transfer_objects.hla.parsing_error_dto import ParsingError
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import ParsingErrorModel
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail


# You need to commit the session to save the changes to the db (db.session.commit())
def add_parsing_error_to_db_session(
        parsing_errors: List[ParsingError], donor_id: int = None, recipient_id: int = None, txm_event_id: int = None
):
    for parsing_error in parsing_errors:
        parsing_error.donor_id=donor_id
        parsing_error.recipient_id=recipient_id
        parsing_error.txm_event_id=txm_event_id

        parsing_error_to_db = ParsingErrorModel(
            hla_code_or_group=parsing_error.hla_code_or_group,
            parsing_issue_detail=parsing_error.parsing_issue_detail,
            message=parsing_error.message,
            donor_id = parsing_error.donor_id,
            recipient_id = parsing_error.recipient_id,
            txm_event_id=parsing_error.txm_event_id,
        )
        db.session.add(parsing_error_to_db)


def add_ids_to_parsing_errors(
        parsing_errors: List[ParsingError], donor_id: int = None, recipient_id: int = None, txm_event_id: int = None
) -> List[ParsingErrorModel]:
    for parsing_error in parsing_errors:
        parsing_error.donor_id=donor_id
        parsing_error.recipient_id=recipient_id
        parsing_error.txm_event_id=txm_event_id
    
    parsing_error_models = [
            ParsingErrorModel(
            hla_code_or_group=parsing_error.hla_code_or_group,
            parsing_issue_detail=parsing_error.parsing_issue_detail,
            message=parsing_error.message,
            donor_id = parsing_error.donor_id,
            recipient_id = parsing_error.recipient_id,
            txm_event_id=parsing_error.txm_event_id
        )
        for parsing_error in parsing_errors]
    return parsing_error_models

def convert_parsing_error_models_to_dataclasses(parsing_error_models: List[ParsingErrorModel]) -> List[ParsingError]:
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


def convert_parsing_error_dataclasses_to_models(parsing_errors: List[ParsingError]) -> List[ParsingErrorModel]:
    return [ParsingErrorModel(
        hla_code_or_group=parsing_error.hla_code_or_group,
        parsing_issue_detail=parsing_error.parsing_issue_detail.name,
        message=parsing_error.message,
        donor_id = parsing_error.donor_id,
        recipient_id = parsing_error.recipient_id,
        txm_event_id=parsing_error.txm_event_id
    ) for parsing_error in parsing_errors if parsing_error.parsing_issue_detail != ParsingIssueDetail.MFI_PROBLEM]


def get_parsing_errors_for_txm_event_id(txm_event_id: int) -> List[ParsingError]:
    return convert_parsing_error_models_to_dataclasses(
        ParsingErrorModel.query.filter(
            ParsingErrorModel.txm_event_id == txm_event_id
        ).all()
    )


def get_parsing_errors_for_patients(txm_event_id: int, donor_ids: List[int] = None, 
                                    recipient_ids: List[int] = None) -> List[ParsingError]:
    if donor_ids is None:
        donor_ids = []
    if recipient_ids is None:
        recipient_ids = []

    parsing_errors = ParsingErrorModel.query.filter(
        and_(ParsingErrorModel.donor_id.in_(donor_ids),
                ParsingErrorModel.txm_event_id == txm_event_id)
    ).all() + ParsingErrorModel.query.filter(
        and_(ParsingErrorModel.recipient_id.in_(recipient_ids),
                ParsingErrorModel.txm_event_id == txm_event_id)
    ).all()

    return convert_parsing_error_models_to_dataclasses(parsing_errors)


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
