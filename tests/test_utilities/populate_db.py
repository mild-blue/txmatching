from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.database.db import db
from txmatching.database.services.app_user_management import persist_user
from txmatching.database.services.patient_service import \
    save_patients_from_excel_to_empty_txm_event
from txmatching.database.sql_alchemy_schema import (AppUserModel, ConfigModel,
                                                    TxmEventModel)
from txmatching.patients.patient import TxmEvent
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app

ADMIN_USER = {
    'email': 'admin@example.com',
    'password': 'admin'
}
VIEWER_USER = {
    'email': 'viewer@example.com',
    'password': 'admin'
}


def create_or_overwrite_txm_event(name: str) -> TxmEvent:
    previous_txm_model = TxmEventModel.query.filter(TxmEventModel.name == name).first()
    if previous_txm_model:
        db.session.delete(previous_txm_model)
        db.session.commit()
    txm_event_model = TxmEventModel(name=name)
    db.session.add(txm_event_model)
    db.session.commit()
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, donors_dict={}, recipients_dict={})


def add_users():
    ConfigModel.query.delete()
    AppUserModel.query.delete()
    app_user = AppUserModel(
        email=ADMIN_USER['email'],
        pass_hash=encode_password(ADMIN_USER['password']),
        role=UserRole.ADMIN,
        second_factor_material=generate_totp_seed(),
        require_2fa=False
    )
    persist_user(app_user)
    ADMIN_USER['id'] = app_user.id
    assert len(AppUserModel.query.all()) == 1
    app_user = AppUserModel(
        email=VIEWER_USER['email'],
        pass_hash=encode_password(VIEWER_USER['password']),
        role=UserRole.VIEWER,
        second_factor_material=generate_totp_seed(),
        require_2fa=False
    )
    persist_user(app_user)
    assert len(AppUserModel.query.all()) == 2


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        patients = parse_excel_data('data.xlsx')
        txm_event = create_or_overwrite_txm_event(name='test')
        save_patients_from_excel_to_empty_txm_event(patients, txm_event_db_id=txm_event.db_id)
        add_users()
