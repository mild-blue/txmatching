from sqlalchemy import and_

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import (DonorModel, RecipientModel,
                                                    TxmEventModel,
                                                    UploadedDataModel)
from txmatching.patients.patient import TxmEvent


def get_newest_txm_event_db_id() -> int:
    txm_event_model = TxmEventModel.query.order_by(TxmEventModel.id.desc()).first()
    if txm_event_model:
        return txm_event_model.id
    else:
        raise ValueError('No TXM event found.')


def create_txm_event(name: str) -> TxmEvent:
    if len(TxmEventModel.query.filter(TxmEventModel.name == name).all()) > 0:
        raise InvalidArgumentException(f'TXM event "{name}" already exists.')
    txm_event_model = TxmEventModel(name=name)
    db.session.add(txm_event_model)
    db.session.commit()
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, donors_dict={}, recipients_dict={})


def delete_txm_event(name: str):
    if len(TxmEventModel.query.filter(TxmEventModel.name == name).all()) == 0:
        raise InvalidArgumentException(f'TXM event "{name}" does not exist.')
    TxmEventModel.query.filter(TxmEventModel.name == name).delete()
    db.session.commit()


def remove_donors_and_recipients_from_txm_event(name: str):
    txm_event_model = TxmEventModel.query.filter(TxmEventModel.name == name).first()
    if not txm_event_model:
        raise InvalidArgumentException(f'No TXM event with name "{name}" found.')
    DonorModel.query.filter(DonorModel.txm_event_id == txm_event_model.id).delete()
    RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event_model.id).delete()


def _remove_last_uploaded_data(txm_event_id: int, current_user_id: int):
    UploadedDataModel.query.filter(and_(UploadedDataModel.txm_event_id == txm_event_id,
                                        UploadedDataModel.user_id == current_user_id)).delete()


def save_original_data(txm_event_name: str, current_user_id: int, data: dict):
    txm_event_model = TxmEventModel.query.filter(TxmEventModel.name == txm_event_name).first()
    if not txm_event_model:
        raise InvalidArgumentException(f'No TXM event with name "{txm_event_name}" found.')
    txm_event_model_id = txm_event_model.id
    _remove_last_uploaded_data(txm_event_model_id, current_user_id)
    uploaded_data_model = UploadedDataModel(
        txm_event_id=txm_event_model_id,
        user_id=current_user_id,
        uploaded_data=data
    )

    db.session.add(uploaded_data_model)
    db.session.commit()
