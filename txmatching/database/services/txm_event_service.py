import logging
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import joinedload, raiseload
from sqlalchemy.orm.exc import NoResultFound

from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import (InvalidArgumentException,
                                        UnauthorizedException)
from txmatching.data_transfer_objects.patients.txm_event_dto_out import \
    TxmEventDTOOut
from txmatching.database.db import db
from txmatching.database.services.patient_service import (
    get_donor_from_donor_model, get_recipient_from_recipient_model)
from txmatching.database.sql_alchemy_schema import (AppUserModel, DonorModel,
                                                    RecipientModel,
                                                    TxmEventModel,
                                                    UploadedDataModel,
                                                    UserToAllowedEvent)
from txmatching.patients.patient import TxmEvent, TxmEventBase
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import TxmEventState
from txmatching.utils.hla_system.hla_transformations.parsing_error import \
    delete_parsing_errors_for_patient
from txmatching.utils.logged_user import get_current_user, get_current_user_id

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
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name,
                    default_config_id=txm_event_model.default_config_id,
                    state=TxmEventState.OPEN, all_donors=[], all_recipients=[])


def delete_txm_event(txm_event_id: int):
    txm_event_to_be_deleted = TxmEventModel.query.filter(TxmEventModel.id == txm_event_id).all()
    if txm_event_to_be_deleted:
        TxmEventModel.query.filter(TxmEventModel.id == txm_event_id).delete()
        db.session.commit()
    else:
        raise InvalidArgumentException(f'No TXM event with id {id} found.')


def remove_donors_and_recipients_from_txm_event_for_country(txm_event_db_id: int, country_code: Country):
    # Remove parsing errors for patients that will be deleted
    donor_ids = [patient_model.id for patient_model in (
        DonorModel.query.filter(and_(DonorModel.txm_event_id == txm_event_db_id,
                                     DonorModel.country == country_code)).all()
    )]
    for donor_id in donor_ids:
        delete_parsing_errors_for_patient(donor_id=donor_id, txm_event_id=txm_event_db_id)

    recipient_ids = [patient_model.id for patient_model in (
        RecipientModel.query.filter(and_(RecipientModel.txm_event_id == txm_event_db_id,
                                         RecipientModel.country == country_code)).all()
    )]
    for recipient_id in recipient_ids:
        delete_parsing_errors_for_patient(recipient_id=recipient_id, txm_event_id=txm_event_db_id)


    DonorModel.query.filter(and_(DonorModel.txm_event_id == txm_event_db_id,
                                 DonorModel.country == country_code)).delete()
    # Very likely is not needed as all recipients should be cascade deleted in the previous step.
    # but to be sure everything gets delted, this stays here.
    RecipientModel.query.filter(and_(RecipientModel.txm_event_id == txm_event_db_id,
                                     RecipientModel.country == country_code)).delete()


def get_txm_event_id_for_current_user() -> int:
    current_user_model = get_current_user()
    allowed_events = get_allowed_txm_event_ids_for_current_user()

    if current_user_model.default_txm_event_id and current_user_model.default_txm_event_id in allowed_events:
        return current_user_model.default_txm_event_id
    else:
        event_id = allowed_events[-1] if len(allowed_events) > 0 else None

        if current_user_model.default_txm_event_id != event_id:
            logger.info(f'Changing default TXM event to {event_id}.')
            current_user_model.default_txm_event_id = event_id
            db.session.commit()

        if event_id is not None:
            return event_id
        else:
            raise ValueError('User has not access to any TXM event.')


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


def get_txm_event_complete(txm_event_db_id: int, load_antibodies_raw: bool = False) -> TxmEvent:
    """
    If load_antibodies_raw is set to False, raw antibodies are not loaded and empty
    lists are returned instead. This is for performance optimization.
    """
    logger.debug(f'Starting to eager load data for TXM event {txm_event_db_id} with '
                 f'load_antibodies_raw={load_antibodies_raw}')
    if load_antibodies_raw:
        loading_options = joinedload(TxmEventModel.donors)
    else:
        loading_options = joinedload(TxmEventModel.donors) \
            .joinedload(DonorModel.recipient) \
            .noload(RecipientModel.hla_antibodies_raw)

    maybe_txm_event_model = TxmEventModel.query.options(loading_options).get(txm_event_db_id)
    logger.debug('Eager loaded data via sql alchemy')

    return _get_txm_event_from_txm_event_model(maybe_txm_event_model)


def get_txm_event_base(txm_event_db_id: int) -> TxmEventBase:
    logger.debug(f'Starting to load data for TXM event {txm_event_db_id}')
    maybe_txm_event_model = TxmEventModel.query.options(raiseload(TxmEventModel.donors)).get(txm_event_db_id)
    logger.debug('Loaded data via sql alchemy')

    return _get_txm_event_base_from_txm_event_model(maybe_txm_event_model)


def _get_txm_event_base_from_txm_event_model(txm_event_model: TxmEventModel) -> TxmEventBase:
    return TxmEventBase(db_id=txm_event_model.id, name=txm_event_model.name,
                        default_config_id=txm_event_model.default_config_id,
                        state=txm_event_model.state)


def _get_txm_event_from_txm_event_model(txm_event_model: TxmEventModel) -> TxmEvent:
    all_donors = sorted([get_donor_from_donor_model(donor_model) for donor_model in txm_event_model.donors],
                        key=lambda donor: donor.db_id)
    logger.debug('Prepared Donors')

    all_recipients = []
    recipient_db_ids = []
    for donor in txm_event_model.donors:
        if donor.recipient is not None and donor.recipient.id not in recipient_db_ids:
            all_recipients.append(get_recipient_from_recipient_model(donor.recipient))
            recipient_db_ids.append(donor.recipient.id)
    all_recipients = sorted(all_recipients, key=lambda recipient: recipient.db_id)

    logger.debug('Prepared Recipients')
    logger.debug('Prepared TXM event')
    return TxmEvent(db_id=txm_event_model.id,
                    name=txm_event_model.name,
                    default_config_id=txm_event_model.default_config_id,
                    state=TxmEventState.OPEN,
                    all_donors=all_donors,
                    all_recipients=all_recipients)


def get_allowed_txm_event_ids_for_current_user() -> List[int]:
    if get_current_user().role == UserRole.ADMIN:
        txm_event_ids = [
            txm_event_model.id for txm_event_model
            in TxmEventModel.query.order_by(TxmEventModel.id.asc()).all()
        ]
    else:
        txm_event_ids = [
            user_to_event_model.txm_event_id for user_to_event_model in
            UserToAllowedEvent.query.filter(
                UserToAllowedEvent.user_id == get_current_user_id()
            ).order_by(
                UserToAllowedEvent.txm_event_id.asc()
            ).all()
        ]

    return txm_event_ids


def set_allowed_txm_event_ids_for_user(user: AppUserModel, txm_event_ids: List[int]):
    if user.role == UserRole.ADMIN:
        logger.warning('Cannot set allowed txm events for admin user. Skipping')
    else:
        UserToAllowedEvent.query.filter(
            UserToAllowedEvent.user_id == user.id
        ).delete()

        for txm_event_id in txm_event_ids:
            if TxmEventModel.query.get(txm_event_id) is None:
                db.session.rollback()
                raise ValueError(f'ID {txm_event_id} should be set as allowed TXM id but such txm event was not found')

            user_to_event = UserToAllowedEvent(user_id=user.id, txm_event_id=txm_event_id)
            db.session.add(user_to_event)

        db.session.commit()


def set_txm_event_state(txm_event_id: int, state: TxmEventState):
    TxmEventModel.query.filter(TxmEventModel.id == txm_event_id).update(
        {'state': state}
    )
    db.session.commit()


def convert_txm_event_base_to_dto(txm_event_base: TxmEventBase) -> TxmEventDTOOut:
    return TxmEventDTOOut(
        id=txm_event_base.db_id,
        name=txm_event_base.name,
        default_config_id=txm_event_base.default_config_id,
        state=txm_event_base.state
    )
