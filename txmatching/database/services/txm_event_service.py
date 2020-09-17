from typing import Union

from txmatching.auth.data_types import FailResponse
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import TxmEventModel
from txmatching.patients.patient import TxmEvent


def get_newest_txm_event_db_id() -> int:
    tx_session_model = TxmEventModel.query.order_by(TxmEventModel.id).first()
    if tx_session_model:
        return tx_session_model.id
    else:
        raise ValueError('No TXM event found')


def create_txm_event(name: str) -> Union[TxmEvent, FailResponse]:
    if len(TxmEventModel.query.filter(TxmEventModel.name == name).all()) > 0:
        raise ValueError("TXM event already exists")
    tx_session_model = TxmEventModel(name=name)
    db.session.add(tx_session_model)
    db.session.commit()
    return TxmEvent(db_id=tx_session_model.id, name=tx_session_model.name, donors_dict={}, recipients_dict={})


def create_or_overwrite_txm_event(name: str) -> TxmEvent:
    previous_txm_model = TxmEventModel.query.filter(TxmEventModel.name == name).first()
    if previous_txm_model:
        db.session.delete(previous_txm_model)
        db.session.commit()
    tx_session_model = TxmEventModel(name=name)
    db.session.add(tx_session_model)
    db.session.commit()
    return TxmEvent(db_id=tx_session_model.id, name=tx_session_model.name, donors_dict={}, recipients_dict={})
