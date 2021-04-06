from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import TxmEventModel
from txmatching.patients.patient import TxmEvent


def create_or_overwrite_txm_event(name: str) -> TxmEvent:
    previous_txm_model = TxmEventModel.query.filter(TxmEventModel.name == name).first()
    if previous_txm_model:
        db.session.delete(previous_txm_model)
        db.session.flush()
    txm_event_model = TxmEventModel(name=name)
    db.session.add(txm_event_model)
    db.session.commit()
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name,
                    default_config_id=txm_event_model.default_config_id,
                    state=txm_event_model.state,
                    all_donors=[], all_recipients=[])
