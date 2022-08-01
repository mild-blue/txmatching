from datetime import datetime
from typing import List

from sqlalchemy import and_

from txmatching.auth.exceptions import (InvalidArgumentException,
                                        OverridingException)
from txmatching.data_transfer_objects.hla.parsing_issue_dto import (
    ParsingIssue, ParsingIssueBase)
from txmatching.data_transfer_objects.patients.utils import \
    parsing_issue_model_to_parsing_issue
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import ParsingIssueModel
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    WARNING_PROCESSING_RESULTS


def confirm_a_parsing_issue(user_id: int, parsing_issue_id: int,
                            txm_event_id: int) -> ParsingIssue:
    parsing_issue = ParsingIssueModel.query.get(parsing_issue_id)

    if parsing_issue is None or parsing_issue.txm_event_id != txm_event_id:
        raise InvalidArgumentException(f'Parsing issue {parsing_issue_id} not found in txm event {txm_event_id}')

    if parsing_issue.parsing_issue_detail not in WARNING_PROCESSING_RESULTS:
        raise InvalidArgumentException(f'Parsing issue {parsing_issue_id} is not a warning')

    if parsing_issue.confirmed_by is not None:
        raise OverridingException(f'Parsing issue {parsing_issue_id} is aready confirmed')

    parsing_issue.confirmed_by = user_id
    parsing_issue.confirmed_at = datetime.now()

    db.session.commit()
    return parsing_issue_model_to_parsing_issue(parsing_issue)


def unconfirm_a_parsing_issue(parsing_issue_id: int, txm_event_id: int) -> ParsingIssue:
    parsing_issue = ParsingIssueModel.query.get(parsing_issue_id)

    if parsing_issue is None or parsing_issue.txm_event_id != txm_event_id:
        raise InvalidArgumentException(f'Parsing issue {parsing_issue_id} not found in txm event {txm_event_id}')

    if parsing_issue.parsing_issue_detail not in WARNING_PROCESSING_RESULTS:
        raise InvalidArgumentException(f'Parsing issue {parsing_issue_id} is not a warning')

    if parsing_issue.confirmed_by is None:
        raise OverridingException(f'Parsing issue {parsing_issue_id} is aready confirmed')

    parsing_issue.confirmed_by = None
    parsing_issue.confirmed_at = None

    db.session.commit()
    return parsing_issue_model_to_parsing_issue(parsing_issue)


def parsing_issues_bases_to_models(
        parsing_issues_temp: List[ParsingIssueBase], donor_id: int = None, recipient_id: int = None, txm_event_id: int = None
) -> List[ParsingIssueModel]:

    parsing_issue_models = [ParsingIssueModel(
        hla_code_or_group=issue_tmp.hla_code_or_group,
        parsing_issue_detail=issue_tmp.parsing_issue_detail,
        message=issue_tmp.message,
        donor_id=donor_id,
        recipient_id=recipient_id,
        txm_event_id=txm_event_id
    ) for issue_tmp in parsing_issues_temp]

    return parsing_issue_models


def convert_parsing_issue_models_to_dataclasses(parsing_issue_models: List[ParsingIssueModel]) -> List[ParsingIssue]:
    return [parsing_issue_model_to_parsing_issue(parsing_issue_model) for parsing_issue_model in parsing_issue_models]



def get_parsing_issues_for_txm_event_id(txm_event_id: int) -> List[ParsingIssue]:
    return convert_parsing_issue_models_to_dataclasses(
        ParsingIssueModel.query.filter(
            ParsingIssueModel.txm_event_id == txm_event_id
        ).all()
    )


def get_parsing_issues_for_patients(txm_event_id: int, donor_ids: List[int] = None,
                                    recipient_ids: List[int] = None) -> List[ParsingIssue]:
    if donor_ids is None:
        donor_ids = []
    if recipient_ids is None:
        recipient_ids = []

    parsing_issues = ParsingIssueModel.query.filter(
        and_(ParsingIssueModel.donor_id.in_(donor_ids),
             ParsingIssueModel.txm_event_id == txm_event_id)
    ).all() + ParsingIssueModel.query.filter(
        and_(ParsingIssueModel.recipient_id.in_(recipient_ids),
             ParsingIssueModel.txm_event_id == txm_event_id)
    ).all()

    return convert_parsing_issue_models_to_dataclasses(parsing_issues)


def delete_parsing_issues_for_patient(
        txm_event_id: int,
        donor_id: int = None,
        recipient_id: int = None,
):
    if recipient_id is not None:
        ParsingIssueModel.query.filter(
            and_(ParsingIssueModel.recipient_id == recipient_id,
                 ParsingIssueModel.txm_event_id == txm_event_id)
        ).delete()
    else:
        ParsingIssueModel.query.filter(
            and_(ParsingIssueModel.donor_id == donor_id,
                 ParsingIssueModel.txm_event_id == txm_event_id)
        ).delete()


def delete_parsing_issues_for_txm_event_id(txm_event_id: int):
    ParsingIssueModel.query.filter(
        ParsingIssueModel.txm_event_id == txm_event_id
    ).delete()