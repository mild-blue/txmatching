from typing import Tuple
from uuid import uuid4

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.auth_management import _change_password
from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import CredentialsMismatchException
from txmatching.auth.user.user_auth_management import register_user
from txmatching.database.services.app_user_management import get_app_user_by_id
from txmatching.database.sql_alchemy_schema import AppUserModel


class TestLoginFlow(DbTests):

    def test__change_password(self):
        usr, current_password = self._create_user()
        new_password = current_password + 'new!'

        _change_password(usr.id, current_password=current_password, new_password=new_password)

        changed_user = get_app_user_by_id(usr.id)
        self.assertTrue(password_matches_hash(changed_user.pass_hash, new_password))
        self.assertFalse(password_matches_hash(usr.pass_hash, current_password))

    def test__change_password_should_fail(self):
        usr, current_password = self._create_user()
        new_password = current_password + 'new!'

        self.assertRaises(CredentialsMismatchException,
                          lambda: _change_password(usr.id,
                                                   current_password=current_password + 'old!',
                                                   new_password=new_password))

        self.assertTrue(password_matches_hash(usr.pass_hash, current_password))
        self.assertFalse(password_matches_hash(usr.pass_hash, new_password))

    def _create_user(self, role: UserRole = UserRole.ADMIN) -> Tuple[AppUserModel, str]:
        pwd = str(uuid4())
        email = str(uuid4())
        register_user(email, pwd, role, '456 678 645')
        db_usr = AppUserModel.query.filter(AppUserModel.email == email).first()
        self.assertIsNotNone(db_usr)
        return db_usr, pwd
