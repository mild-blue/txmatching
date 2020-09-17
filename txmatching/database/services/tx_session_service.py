from typing import Union

from txmatching.auth.data_types import FailResponse
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import TxSessionModel
from txmatching.patients.patient import TxSession


def get_newest_tx_session() -> TxSessionModel:
    tx_session_model = TxSessionModel.query.order_by(TxSessionModel.created_at).first()
    if tx_session_model:
        return tx_session_model
    else:
        raise ValueError('No session found')


def create_tx_session(name: str) -> Union[TxSession, FailResponse]:
    if len(TxSessionModel.query.filter(TxSessionModel.name == name)) > 0:
        return FailResponse('Tx session already exists')
    tx_session_model = TxSessionModel(name=name)
    db.session.add(tx_session_model)
    db.session.commit()
    return TxSession(db_id=tx_session_model.id, name=tx_session_model.name, donors_dict={}, recipients_dict={})


def create_or_ovewrite_tx_session(name: str) -> TxSession:
    TxSessionModel.query.filter(TxSessionModel.name == name).delete()
    db.session.commit()
    tx_session_model = TxSessionModel(name=name)
    db.session.add(tx_session_model)
    db.session.commit()
    return TxSession(db_id=tx_session_model.id, name=tx_session_model.name, donors_dict={}, recipients_dict={})
