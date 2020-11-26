from typing import Tuple
from unittest import mock
from uuid import uuid4

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import UserUpdateException, InvalidAuthCallException
from txmatching.auth.user.user_auth_management import register_user, change_user_password
from txmatching.configuration.app_configuration.application_configuration import ApplicationEnvironment
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.utils.enums import Country


class TestUserCrudWithDb(DbTests):
    def _create_and_get(self, role: UserRole = UserRole.ADMIN) -> Tuple[AppUserModel, str]:
        pwd = str(uuid4())
        email = str(uuid4()) + "abc"

        app_config = mock.MagicMock()
        app_config.environment = ApplicationEnvironment.PRODUCTION

        def get_app_config():
            return app_config

        with mock.patch('txmatching.auth.user.user_auth_management.get_application_configuration', get_app_config):
            # check that we normalize email to lower
            register_user(email.upper(), pwd, [Country.CZE], role, '+420456678645')

        db_usr = AppUserModel.query.filter(AppUserModel.email == email).first()
        self.assertIsNotNone(db_usr)
        self.assertNotEqual(pwd, db_usr.pass_hash)
        self.assertTrue(db_usr.require_2fa)
        return db_usr, pwd

    def test_register_user(self):
        db_usr, pwd = self._create_and_get()
        self.assertTrue(password_matches_hash(db_usr.pass_hash, pwd))

    def test_register_user_on_staging(self):
        email = str(uuid4())

        app_config = mock.MagicMock()
        app_config.environment = ApplicationEnvironment.STAGING

        def get_app_config():
            return app_config

        with mock.patch('txmatching.auth.user.user_auth_management.get_application_configuration', get_app_config):
            # check that we normalize email to lower
            register_user(email, str(uuid4()), [], UserRole.ADMIN, '+420456678645')

        db_usr = AppUserModel.query.filter(AppUserModel.email == email).first()
        self.assertIsNotNone(db_usr)
        self.assertFalse(db_usr.require_2fa)

    def test_change_user_password(self):
        usr, old_pwd = self._create_and_get()
        self.assertTrue(password_matches_hash(usr.pass_hash, old_pwd))

        new_pwd = str(uuid4())
        change_user_password(usr.id, new_pwd)

        usr = AppUserModel.query.get(usr.id)
        self.assertIsNotNone(usr)

        self.assertTrue(password_matches_hash(usr.pass_hash, new_pwd))
        self.assertFalse(password_matches_hash(usr.pass_hash, old_pwd))

    def test_register_user_should_fail_invalid_phone(self):
        invalid_phones = [
            '',  # empty string
            '721345678',  # missing international code
            '00420712345678',  # wrong format of the code, we enforce +420
            '+420 721 567 876',  # spaces inside,
            '+42072156787a',  # character inside the string
        ]
        for phone in invalid_phones:
            self.assertRaises(UserUpdateException,
                              lambda: register_user(str(uuid4()), str(uuid4()), [], UserRole.ADMIN,
                                                    phone_number=phone))

    def test_create_as_service(self):
        self.assertRaises(InvalidAuthCallException,
                          lambda: register_user(str(uuid4()), str(uuid4()), [], UserRole.SERVICE, '+123456789'))
