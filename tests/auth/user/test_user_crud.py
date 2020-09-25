from typing import Tuple
from uuid import uuid4

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import UserUpdateException
from txmatching.auth.user.user_crud import register_user, change_user_password
from txmatching.database.sql_alchemy_schema import AppUserModel


class Test(DbTests):
    def _create_and_get(self, role: UserRole = UserRole.ADMIN) -> Tuple[AppUserModel, str]:
        pwd = str(uuid4())
        email = str(uuid4())
        register_user(email, pwd, role, '456 678 645')
        db_usr = AppUserModel.query.filter(AppUserModel.email == email).first()
        self.assertIsNotNone(db_usr)
        self.assertNotEqual(pwd, db_usr.pass_hash)
        return db_usr, pwd

    def test_register_user(self):
        db_usr, pwd = self._create_and_get()
        self.assertTrue(password_matches_hash(db_usr.pass_hash, pwd))

    def test_change_user_password(self):
        usr, old_pwd = self._create_and_get()
        self.assertTrue(password_matches_hash(usr.pass_hash, old_pwd))

        new_pwd = str(uuid4())
        change_user_password(usr.id, new_pwd)

        usr = AppUserModel.query.get(usr.id)
        self.assertIsNotNone(usr)

        self.assertTrue(password_matches_hash(usr.pass_hash, new_pwd))
        self.assertFalse(password_matches_hash(usr.pass_hash, old_pwd))

    def test_create_without_pohone(self):
        self.assertRaises(UserUpdateException,
                          lambda: register_user(str(uuid4()), str(uuid4()), UserRole.ADMIN, ''))

    def test_create_as_service(self):
        self.assertRaises(AssertionError,
                          lambda: register_user('', '', UserRole.SERVICE, ''))
