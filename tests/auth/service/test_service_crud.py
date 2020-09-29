from typing import Tuple
from uuid import uuid4

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.exceptions import UserUpdateException
from txmatching.auth.service.service_auth_management import register_service, change_service_password
from txmatching.database.sql_alchemy_schema import AppUserModel


class TestServiceCrudWithDb(DbTests):

    def _create_and_get(self) -> Tuple[AppUserModel, str]:
        pwd = str(uuid4())
        email = str(uuid4())
        register_service(email, pwd, '1.1.1.1')
        db_usr = AppUserModel.query.filter(AppUserModel.email == email).first()
        self.assertIsNotNone(db_usr)
        self.assertNotEqual(pwd, db_usr.pass_hash)
        return db_usr, pwd

    def test_register_service(self):
        db_usr, pwd = self._create_and_get()
        self.assertTrue(password_matches_hash(db_usr.pass_hash, pwd))

    def test_change_service_password(self):
        usr, old_pwd = self._create_and_get()
        self.assertTrue(password_matches_hash(usr.pass_hash, old_pwd))

        new_pwd = str(uuid4())
        change_service_password(usr.id, new_pwd)

        usr = AppUserModel.query.get(usr.id)
        self.assertIsNotNone(usr)

        self.assertTrue(password_matches_hash(usr.pass_hash, new_pwd))
        self.assertFalse(password_matches_hash(usr.pass_hash, old_pwd))

    def test_create_with_invalid_ip(self):
        self.assertRaises(UserUpdateException,
                          lambda: register_service(str(uuid4()), str(uuid4()), '1'))

    def test_create_with_empty_pwd(self):
        self.assertRaises(UserUpdateException,
                          lambda: register_service(str(uuid4()), '', '1.1.1.1'))
