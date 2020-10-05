from typing import List

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
    'password': 'viewer'
}

OTP_USER = {
    'email': 'otp@example.com',
    'password': 'admin'
}

SERVICE_USER = {
    'email': 'service@example.com',
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
    admin = AppUserModel(
        email=ADMIN_USER['email'],
        pass_hash=encode_password(ADMIN_USER['password']),
        role=UserRole.ADMIN,
        second_factor_material=generate_totp_seed(),
        require_2fa=False
    )
    viewer = AppUserModel(
        email=VIEWER_USER['email'],
        pass_hash=encode_password(VIEWER_USER['password']),
        role=UserRole.VIEWER,
        second_factor_material=generate_totp_seed(),
        require_2fa=False
    )
    otp = AppUserModel(
        email=OTP_USER['email'],
        pass_hash=encode_password(OTP_USER['password']),
        role=UserRole.ADMIN,
        second_factor_material=generate_totp_seed(),
        phone_number='123456789',
        require_2fa=True
    )
    service = AppUserModel(
        email=SERVICE_USER['email'],
        pass_hash=encode_password(SERVICE_USER['password']),
        role=UserRole.SERVICE,
        second_factor_material=generate_totp_seed(),
        require_2fa=False
    )
    _add_users([admin, viewer, otp, service])
    ADMIN_USER['id'] = admin.id
    VIEWER_USER['id'] = viewer.id
    OTP_USER['id'] = otp.id
    SERVICE_USER['id'] = service.id


def _add_users(users: List[AppUserModel]):
    for u in users:
        persist_user(u)
    assert len(AppUserModel.query.all()) == len(users)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        patients = parse_excel_data('patient_data_2020_07_obfuscated.xlsx')
        txm_event = create_or_overwrite_txm_event(name='test')
        save_patients_from_excel_to_empty_txm_event(patients, txm_event_db_id=txm_event.db_id)
        add_users()
