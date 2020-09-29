from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import TxmEventModel
from txmatching.patients.patient import TxmEvent


def get_newest_txm_event_db_id() -> int:
    txm_event_model = TxmEventModel.query.order_by(TxmEventModel.id.desc()).first()
    if txm_event_model:
        return txm_event_model.id
    else:
        raise ValueError('No TXM event found')


def create_txm_event(name: str) -> TxmEvent:
    if len(TxmEventModel.query.filter(TxmEventModel.name == name).all()) > 0:
        raise ValueError("TXM event already exists")
    txm_event_model = TxmEventModel(name=name)
    db.session.add(txm_event_model)
    db.session.commit()
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, donors_dict={}, recipients_dict={})
