from typing import Optional

from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import TxSessionModel
from txmatching.patients.patient import TxSession
from txmatching.database.services import patient_service


def get_newest_tx_session() -> TxSessionModel:
    tx_session_model = TxSessionModel.query.order_by(TxSessionModel.created_at).first()
    if tx_session_model:
        return tx_session_model
    else:
        raise ValueError("No session found")


def create_or_ovewrite_tx_session(name: str):
    TxSessionModel.query.filter(TxSessionModel.name == name).delete()
    db.session.commit()
    tx_session_model = TxSessionModel(name=name)
    db.session.add(tx_session_model)
    db.session.commit()
    return TxSession(db_id=tx_session_model.id, name=tx_session_model.name, donors_dict={}, recipients_dict={})


def get_tx_session(session_db_id: Optional[int] = None) -> TxSession:
    if session_db_id is None:
        tx_session = get_newest_tx_session()
    else:
        tx_session = TxSessionModel.query.get(session_db_id)

    active_donors = tx_session.donors
    active_recipients = tx_session.recipients
    donors_with_recipients = [(donor_model.recipient_id, patient_service.get_donor_from_donor_model(donor_model))
                              for donor_model in active_donors]

    donors_dict = {donor.db_id: donor for _, donor in donors_with_recipients}
    donors_with_recipients_dict = {related_recipient_id: donor for related_recipient_id, donor in donors_with_recipients
                                   if related_recipient_id is not None}

    recipients_dict = {
        recipient_model.id: patient_service.get_recipient_from_recipient_model(
            recipient_model, donors_with_recipients_dict)
        for recipient_model in active_recipients}

    return TxSession(db_id=tx_session.id, name=tx_session.name, donors_dict=donors_dict,
                     recipients_dict=recipients_dict)
