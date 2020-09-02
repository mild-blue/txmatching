import os
import unittest
from importlib import util as importing

from flask import Flask
from flask_restx import Api

from tests.test_utilities.populate_db import ADMIN_USER, add_users
from txmatching.database.db import db
from txmatching.database.services.patient_service import save_patients
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import user_api
from txmatching.web.auth.login_check import store_user_in_context


class DbTests(unittest.TestCase):
    _database_name = 'memory.sqlite'

    def setUp(self):
        """
        Creates a new database for the unit test to use
        """

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self._database_name}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)

        self.app.app_context().push()
        self._load_local_development_config()

        db.create_all()

        add_users()

        self._set_bearer_token()

    def fill_db_with_patients_and_results(self):
        self.fill_db_with_patients()
        solve_from_db()

    @staticmethod
    def fill_db_with_patients(file='test_utilities/data.xlsx'):
        patients = parse_excel_data(file)
        save_patients(patients)

    def _set_bearer_token(self):
        self.api = Api(self.app)
        self.api.add_namespace(user_api, path='/user')
        with self.app.test_client() as client:
            json = client.post('/user/login',
                               json={'email': ADMIN_USER['email'], 'password': ADMIN_USER['password']}).json
            token = json['auth_token']
            self.auth_headers = {'Authorization': f'Bearer {token}'}
            store_user_in_context(ADMIN_USER['id'])

    def _load_local_development_config(self):
        config_file = 'txmatching.web.local_config'
        if importing.find_spec(config_file):
            self.app.config.from_object(config_file)

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with self.app.app_context():
            db.drop_all()

        if os.path.exists(f'test_utilities/{self._database_name}'):
            os.remove(f'test_utilities/{self._database_name}')
