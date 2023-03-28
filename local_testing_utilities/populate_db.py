import logging
from typing import List

from local_testing_utilities.generate_patients import (
    CROSSMATCH_TXM_EVENT_NAME, GENERATED_TXM_EVENT_NAME, SMALL_DATA_FOLDER,
    SMALL_DATA_FOLDER_MULTIPLE_DONORS, SMALL_DATA_FOLDER_THEORETICAL,
    SMALL_DATA_FOLDER_WITH_CROSSMATCH, store_generated_patients_from_folder)
from local_testing_utilities.utils import create_or_overwrite_txm_event
from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.app_user_management import persist_user
from txmatching.database.services.config_service import \
    save_config_parameters_to_db
from txmatching.database.services.pairing_result_service import \
    solve_from_configuration_and_save
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_excel
from txmatching.database.services.scorer_service import \
    matchings_model_from_dict
from txmatching.database.services.txm_event_service import (
    get_txm_event_complete, set_allowed_txm_event_ids_for_user)
from txmatching.database.sql_alchemy_schema import AppUserModel, ConfigModel
from txmatching.utils.country_enum import Country
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path

ALLOWED_EDIT_COUNTRIES = 'allowed_edit_countries'
PATIENT_DATA_OBFUSCATED = 'tests/resources/patient_data_2020_07_obfuscated_multi_country.xlsx'
PASSWORD = 'admin'
PASSWORD_HASH = encode_password(PASSWORD)
logger = logging.getLogger(__name__)
ADMIN_USER = {
    'email': 'admin@example.com',
    'password_hash': PASSWORD_HASH,
    'password': PASSWORD,
    'role': UserRole.ADMIN,
    'require_2fa': False
}

TEST_USER = {
    'email': 'test@example.com',
    'password_hash': PASSWORD_HASH,
    'password': PASSWORD,
    'role': UserRole.VIEWER,
    'require_2fa': False
}

VIEWER_USER = {
    'email': 'viewer@example.com',
    'password_hash': PASSWORD_HASH,
    'password': PASSWORD,
    'role': UserRole.VIEWER,
    'require_2fa': False,
    'allowed_txm_events': [1]
}

OTP_USER = {
    'email': 'otp@example.com',
    'password_hash': PASSWORD_HASH,
    'password': PASSWORD,
    'role': UserRole.ADMIN,
    'phone_number': '123456789',
    'require_2fa': False
}

SERVICE_USER = {
    'email': 'service@example.com',
    'password_hash': PASSWORD_HASH,
    'password': PASSWORD,
    'role': UserRole.SERVICE,
    'require_2fa': False,
    'default_txm_event_id': 1,
    'allowed_txm_events': [1, 2]
}
ADMIN_WITH_DEFAULT_TXM_EVENT = {
    'email': 'admin_default_txm_event@example.com',
    'password_hash': PASSWORD_HASH,
    'password': PASSWORD,
    'role': UserRole.ADMIN,
    'require_2fa': False,
    'default_txm_event_id': 1
}

EDITOR_WITH_ONLY_ONE_COUNTRY = {
    'email': 'editor_only_one_country@example.com',
    'password_hash': PASSWORD_HASH,
    'password': PASSWORD,
    'role': UserRole.EDITOR,
    'require_2fa': False,
    'allowed_txm_events': [1, 2],
    'default_txm_event_id': 1,
    ALLOWED_EDIT_COUNTRIES: [Country.CZE]
}
USERS = [
    ADMIN_USER, TEST_USER, SERVICE_USER, OTP_USER, ADMIN_WITH_DEFAULT_TXM_EVENT,
    VIEWER_USER, EDITOR_WITH_ONLY_ONE_COUNTRY
]


def add_users():
    ConfigModel.query.delete()
    AppUserModel.query.delete()
    user_models = []
    for user in USERS:
        if ALLOWED_EDIT_COUNTRIES not in user:
            user[ALLOWED_EDIT_COUNTRIES] = list(Country)
        user_model = AppUserModel(
            email=user.get('email'),
            pass_hash=user.get('password_hash'),
            role=user.get('role'),
            second_factor_material=generate_totp_seed(),
            phone_number=user.get('phone_number'),
            require_2fa=user.get('require_2fa'),
            default_txm_event_id=user.get('default_txm_event_id'),
            allowed_edit_countries=user.get(ALLOWED_EDIT_COUNTRIES)
        )
        user_models.append(user_model)

    _add_users(user_models)
    for user, user_model in zip(USERS, user_models):
        user['id'] = user_model.id
    return user_models


def add_allowed_events_to_users(user_models: List[AppUserModel]):
    for user, user_model in zip(USERS, user_models):
        allowed_txm_events = user.get('allowed_txm_events')
        if allowed_txm_events:
            set_allowed_txm_event_ids_for_user(user_model, allowed_txm_events)


def _add_users(users: List[AppUserModel]):
    for user in users:
        persist_user(user)
    assert len(AppUserModel.query.all()) == len(users)


def populate_db_with_data(user_models):
    txm_event = create_or_overwrite_txm_event(name='mock_data_CZE_CAN_IND')
    add_allowed_events_to_users(user_models)
    patients = parse_excel_data(get_absolute_path(PATIENT_DATA_OBFUSCATED), country=None,
                                txm_event_name='mock_data_CZE_CAN_IND')

    replace_or_add_patients_from_excel(patients)

    txm_event = get_txm_event_complete(txm_event.db_id)

    configuration_parameters = ConfigParameters(
        max_sequence_length=100,
        max_cycle_length=100,
        use_high_resolution=True
    )

    configuration = save_config_parameters_to_db(config_parameters=configuration_parameters,
                                                 txm_event_id=txm_event.db_id,
                                                 user_id=1)

    pairing_result_model = solve_from_configuration_and_save(configuration=configuration,
                                                             txm_event=txm_event)

    matchings_model = matchings_model_from_dict(pairing_result_model.calculated_matchings)

    logger.info(f'Successfully stored {len(matchings_model.matchings)} matchings into the database.')


def populate_small_db():
    create_or_overwrite_txm_event(name='test')
    create_or_overwrite_txm_event(name=CROSSMATCH_TXM_EVENT_NAME)

    add_users()
    store_generated_patients_from_folder(SMALL_DATA_FOLDER, GENERATED_TXM_EVENT_NAME)
    store_generated_patients_from_folder(SMALL_DATA_FOLDER_WITH_CROSSMATCH, CROSSMATCH_TXM_EVENT_NAME)


def populate_db_multiple_recipients():
    create_or_overwrite_txm_event(name=CROSSMATCH_TXM_EVENT_NAME)
    add_users()
    store_generated_patients_from_folder(SMALL_DATA_FOLDER_MULTIPLE_DONORS, GENERATED_TXM_EVENT_NAME)


def populate_db_theoretical_double_crossmach():
    create_or_overwrite_txm_event(name=CROSSMATCH_TXM_EVENT_NAME)
    add_users()
    store_generated_patients_from_folder(SMALL_DATA_FOLDER_THEORETICAL, GENERATED_TXM_EVENT_NAME)


def populate_large_db():
    create_or_overwrite_txm_event(name='test')
    user_models = add_users()
    populate_db_with_data(user_models)
    store_generated_patients_from_folder()
