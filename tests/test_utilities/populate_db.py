import logging
from typing import List

from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.configuration.configuration import Configuration
from txmatching.database.db import db
from txmatching.database.services.app_user_management import persist_user
from txmatching.database.services.patient_service import \
    save_patients_from_excel_to_txm_event
from txmatching.database.sql_alchemy_schema import (AppUserModel, ConfigModel,
                                                    TxmEventModel)
from txmatching.patients.patient import TxmEvent
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import Country
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app

logger = logging.getLogger(__name__)
ADMIN_USER = {
    'email': 'admin@example.com',
    'password': 'admin',
    'role': UserRole.ADMIN,
    'require_2fa': False
}
VIEWER_USER = {
    'email': 'viewer@example.com',
    'password': 'viewer',
    'role': UserRole.VIEWER,
    'require_2fa': False
}

OTP_USER = {
    'email': 'otp@example.com',
    'password': 'admin',
    'role': UserRole.ADMIN,
    'phone_number': '123456789',
    'require_2fa': False
}

SERVICE_USER = {
    'email': 'service@example.com',
    'password': 'admin',
    'role': UserRole.SERVICE,
    'require_2fa': False,
    'default_txm_event_id': 1
}
ADMIN_WITH_DEFAULT_TXM_EVENT = {
    'email': 'admin_default_txm_event@example.com',
    'password': 'admin',
    'role': UserRole.ADMIN,
    'require_2fa': False,
    'default_txm_event_id': 1
}
USERS = [
    ADMIN_USER, SERVICE_USER, OTP_USER, ADMIN_WITH_DEFAULT_TXM_EVENT, VIEWER_USER
]


def create_or_overwrite_txm_event(name: str) -> TxmEvent:
    previous_txm_model = TxmEventModel.query.filter(TxmEventModel.name == name).first()
    if previous_txm_model:
        db.session.delete(previous_txm_model)
        db.session.flush()
    txm_event_model = TxmEventModel(name=name)
    db.session.add(txm_event_model)
    db.session.commit()
    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, all_donors=[], all_recipients=[])


def add_users():
    ConfigModel.query.delete()
    AppUserModel.query.delete()
    user_models = []
    for user in USERS:
        user_model = AppUserModel(
            email=user.get('email'),
            pass_hash=encode_password(user.get('password')),
            role=user.get('role'),
            second_factor_material=generate_totp_seed(),
            phone_number=user.get('phone_number'),
            require_2fa=user.get('require_2fa'),
            default_txm_event_id=user.get('default_txm_event_id'),
            allowed_edit_countries=[country for country in Country]
        )
        user_models.append(user_model)

    _add_users(user_models)
    for user, user_model in zip(USERS, user_models):
        user['id'] = user_model.id


def _add_users(users: List[AppUserModel]):
    for u in users:
        persist_user(u)
    assert len(AppUserModel.query.all()) == len(users)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_or_overwrite_txm_event(name='test')
        patients = parse_excel_data('../resources/patient_data_2020_07_obfuscated.xlsx')
        txm_event = create_or_overwrite_txm_event(name='mock_data_CZE_CAN_IND')
        save_patients_from_excel_to_txm_event(patients, txm_event_db_id=txm_event.db_id)
        add_users()
        result = solve_from_configuration(txm_event_db_id=txm_event.db_id,
                                          configuration=Configuration(max_sequence_length=100, max_cycle_length=100,
                                                                      use_split_resolution=True))
        logger.info(f'Successfully stored {len(list(result.calculated_matchings))} matchings into the database.')
