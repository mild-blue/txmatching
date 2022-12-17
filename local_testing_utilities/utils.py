from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import TxmEventModel
from txmatching.patients.patient import StrictnessType, TxmEvent


def create_or_overwrite_txm_event(name: str, strictness_type: StrictnessType = StrictnessType.STRICT) -> TxmEvent:
    previous_txm_model = TxmEventModel.query.filter(TxmEventModel.name == name).first()
    if previous_txm_model:
        db.session.delete(previous_txm_model)
        db.session.flush()
    txm_event_model = TxmEventModel(name=name, strictness_type=strictness_type)
    db.session.add(txm_event_model)
    db.session.commit()
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name,
                    default_config_id=txm_event_model.default_config_id,
                    state=txm_event_model.state, strictness_type=strictness_type,
                    all_donors=[], all_recipients=[])
