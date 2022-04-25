import logging
import os
import unittest
from importlib import util as importing
from typing import Dict

from flask import Flask
from flask_restx import Api
from sqlalchemy import event
from sqlalchemy.engine import Engine

from local_testing_utilities.populate_db import (ADMIN_USER, SERVICE_USER,
                                                 VIEWER_USER, add_users)
from local_testing_utilities.utils import create_or_overwrite_txm_event
from txmatching.auth.auth_check import store_user_in_context
from txmatching.auth.data_types import UserRole
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.db import db
from txmatching.database.services.config_service import \
    save_config_parameters_to_db
from txmatching.database.services.pairing_result_service import \
    solve_from_configuration_and_save
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_excel
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import (API_VERSION, USER_NAMESPACE, add_all_namespaces,
                            register_error_handlers)

ROLE_CREDENTIALS = {
    UserRole.ADMIN: ADMIN_USER,
    UserRole.VIEWER: VIEWER_USER,
    UserRole.EDITOR: None,
    UserRole.SERVICE: SERVICE_USER
}


# adds foreign key support to test database
@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


class DbTests(unittest.TestCase):
    _database_name = 'memory.sqlite'

    def setUp(self):
        formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        logging.basicConfig(level=logging.DEBUG, format=formatter)
        """
        Creates a new database for the unit test to use
        """
        # delete file from previous test run in case it was forgotten there
        if os.path.exists(get_absolute_path(f'/tests/test_utilities/{self._database_name}')):
            os.remove(get_absolute_path(f'/tests/test_utilities/{self._database_name}'))

        self.app = Flask(__name__)
        self.app.config['ENVIRONMENT'] = 'DEVELOPMENT'
        self.app.config['USE_2FA'] = 'true'
        self.app.config['SMS_SERVICE_URL'] = 'url'
        self.app.config['SMS_SERVICE_SENDER'] = 'sender'
        self.app.config['SMS_SERVICE_LOGIN'] = 'login'
        self.app.config['SMS_SERVICE_PASSWORD'] = 'pass'
        self.app.config['SERVER_NAME'] = 'test'
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self._database_name}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SQLALCHEMY_ECHO'] = False  # Enable if you want to see DB queries.
        db.init_app(self.app)

        self.app.app_context().push()
        self._load_local_development_config()

        db.create_all()

        self.app.app_context().push()
        self.api = Api(self.app)
        add_all_namespaces(self.api)
        register_error_handlers(self.api)

        add_users()

        self._set_bearer_token()

    def fill_db_with_patients_and_results(self) -> int:
        txm_event_db_id = self.fill_db_with_patients()
        txm_event = get_txm_event_complete(txm_event_db_id)
        configuration_parameters = ConfigParameters()
        configuration = save_config_parameters_to_db(
            config_parameters=configuration_parameters,
            txm_event_id=txm_event_db_id,
            user_id=1
        )
        solve_from_configuration_and_save(
            configuration=configuration,
            txm_event=txm_event
        )
        return txm_event_db_id

    @staticmethod
    def fill_db_with_patients(file=get_absolute_path('/tests/resources/data.xlsx'), txm_event='test') -> int:
        patients = parse_excel_data(file, txm_event, None)
        txm_event = create_or_overwrite_txm_event(name=txm_event)
        replace_or_add_patients_from_excel(patients)
        return txm_event.db_id

    def _set_bearer_token(self):
        self.login_with_role(UserRole.ADMIN)

    def login_with_credentials(self, credentials: Dict):
        self.login_with(
            email=credentials['email'],
            password=credentials['password'],
            user_id=credentials['id'],
            user_role=credentials['role']
        )

    def login_with_role(self, user_role: UserRole):
        credentials = ROLE_CREDENTIALS[user_role]
        self.login_with_credentials(credentials)

    def login_with(self, email: str, password: str, user_id: int, user_role: UserRole):
        with self.app.test_client() as client:
            json = client.post(f'{API_VERSION}/{USER_NAMESPACE}/login',
                               json={'email': email, 'password': password}).json
            token = json['auth_token']
            self.auth_headers = {'Authorization': f'Bearer {token}'}
            store_user_in_context(user_id, user_role)

    def _load_local_development_config(self):
        config_file = 'txmatching.web.local_config'
        if importing.find_spec(config_file):
            self.app.config.from_object(config_file)

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with self.app.app_context():
            db.session.rollback()
            db.drop_all()

        if os.path.exists(get_absolute_path(f'/tests/test_utilities/{self._database_name}')):
            os.remove(get_absolute_path(f'/tests/test_utilities/{self._database_name}'))
