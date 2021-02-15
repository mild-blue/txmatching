import logging
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import joinedload, raiseload
from sqlalchemy.orm.exc import NoResultFound

from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import (InvalidArgumentException,
                                        UnauthorizedException)
from txmatching.database.db import db
from txmatching.database.services.patient_service import (
    get_donor_from_donor_model, get_recipient_from_recipient_model)
from txmatching.database.sql_alchemy_schema import (DonorModel, RecipientModel,
                                                    TxmEventModel,
                                                    UploadedDataModel)
from txmatching.patients.patient import TxmEvent, TxmEventBase
from txmatching.utils.country_enum import Country
from txmatching.utils.logged_user import get_current_user

logger = logging.getLogger(__name__)


def get_newest_txm_event_db_id() -> int:
    txm_event_model = TxmEventModel.query.order_by(TxmEventModel.id.desc()).first()
    if txm_event_model:
        return txm_event_model.id
    else:
        raise ValueError('There are no TXM events in the database.')


def create_txm_event(name: str) -> TxmEvent:
    if len(TxmEventModel.query.filter(TxmEventModel.name == name).all()) > 0:
        raise InvalidArgumentException(f'TXM event "{name}" already exists.')
    txm_event_model = TxmEventModel(name=name)
    db.session.add(txm_event_model)
    db.session.commit()
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, all_donors=[], all_recipients=[])


def delete_txm_event(name: str):
    txm_event_db_id = get_txm_event_db_id_by_name(name)
    TxmEventModel.query.filter(TxmEventModel.id == txm_event_db_id).delete()
    db.session.commit()


def remove_donors_and_recipients_from_txm_event_for_country(txm_event_db_id: int, country_code: Country):
    DonorModel.query.filter(and_(DonorModel.txm_event_id == txm_event_db_id,
                                 DonorModel.country == country_code)).delete()
    # Very likely is not needed as all recipients should be cascade deleted in the previous step.
    # but to be sure everything gets delted, this stays here.
    RecipientModel.query.filter(and_(RecipientModel.txm_event_id == txm_event_db_id,
                                     RecipientModel.country == country_code)).delete()


def get_txm_event_id_for_current_user() -> int:
    current_user_model = get_current_user()
    # TODO change in https://trello.com/c/xRmQhnqM
    if current_user_model.default_txm_event_id:
        return current_user_model.default_txm_event_id
    else:
        return get_newest_txm_event_db_id()


def update_default_txm_event_id_for_current_user(event_id: int):
    if event_id not in get_allowed_txm_event_ids_for_current_user():
        raise UnauthorizedException(f'TXM event {event_id} is not allowed for this user.')

    current_user_model = get_current_user()
    current_user_model.default_txm_event_id = event_id
    db.session.commit()


def save_original_data(txm_event_name: str, current_user_id: int, data: dict):
    txm_event_db_id = get_txm_event_db_id_by_name(txm_event_name)
    uploaded_data_model = UploadedDataModel(
        txm_event_id=txm_event_db_id,
        user_id=current_user_id,
        uploaded_data=data
    )

    db.session.add(uploaded_data_model)
    db.session.commit()


def get_txm_event_db_id_by_name(txm_event_name: str) -> int:
    try:
        txm_event_model = TxmEventModel.query.filter(TxmEventModel.name == txm_event_name).one()
        return txm_event_model.id
    except NoResultFound as error:
        raise InvalidArgumentException(f'No TXM event with name "{txm_event_name}" found.') from error


def get_txm_event_complete(txm_event_db_id: int) -> TxmEvent:
    logger.debug(f'Starting to eager load data for TXM event {txm_event_db_id}')
    maybe_txm_event_model = TxmEventModel.query.options(joinedload(TxmEventModel.donors)).get(txm_event_db_id)
    logger.debug('Eager loaded data via sql alchemy')

    return _get_txm_event_from_txm_event_model(maybe_txm_event_model)


def get_txm_event_base(txm_event_db_id: int) -> TxmEventBase:
    logger.debug(f'Starting to load data for TXM event {txm_event_db_id}')
    maybe_txm_event_model = TxmEventModel.query.options(raiseload(TxmEventModel.donors)).get(txm_event_db_id)
    logger.debug('Loaded data via sql alchemy')

    return _get_txm_event_base_from_txm_event_model(maybe_txm_event_model)


def _get_txm_event_base_from_txm_event_model(txm_event_model: TxmEventModel) -> TxmEventBase:
    return TxmEventBase(db_id=txm_event_model.id, name=txm_event_model.name)


def _get_txm_event_from_txm_event_model(txm_event_model: TxmEventModel) -> TxmEvent:
    all_donors = sorted([get_donor_from_donor_model(donor_model) for donor_model in txm_event_model.donors],
                        key=lambda donor: donor.db_id)
    logger.debug('Prepared Donors')
    all_recipients = sorted([get_recipient_from_recipient_model(donor.recipient, donor.id)
                             for donor in txm_event_model.donors if donor.recipient is not None],
                            key=lambda recipient: recipient.db_id)
    logger.debug('Prepared Recipients')
    logger.debug('Prepared TXM event')
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, all_donors=all_donors,
                    all_recipients=all_recipients)


def get_allowed_txm_event_ids_for_current_user() -> List[int]:
    if get_current_user().role == UserRole.ADMIN:
        txm_event_ids = [
            txm_event_model.id for txm_event_model
            in TxmEventModel.query.order_by(TxmEventModel.id.asc()).all()
        ]
        return txm_event_ids
    else:
        return [get_txm_event_id_for_current_user()]
