from typing import List
from uuid import uuid4

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.database.services.app_user_management import persist_user, get_app_user_by_email
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.utils.enums import Country


class TestAppUserManagementWithDb(DbTests):

    def test_persist_user_with_some_countries(self):
        self._run_countries_test([Country.CZE])

    def test_persist_user_with_all_countries(self):
        # noinspection PyTypeChecker
        # because Pycharm confuses Enum with strings sometimes
        self._run_countries_test([country for country in Country])

    def _run_countries_test(self, allowed_countries: List[Country]):
        user = AppUserModel(
            email=str(uuid4),
            pass_hash=encode_password('password'),
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            require_2fa=False,
            allowed_edit_countries=allowed_countries
        )

        self.assertEqual(len(allowed_countries), len(user.allowed_edit_countries))
        for allowed in allowed_countries:
            self.assertTrue(allowed in user.allowed_edit_countries)

        persist_user(user)

        db_user = get_app_user_by_email(user.email)

        self.assertEqual(len(allowed_countries), len(db_user.allowed_edit_countries))
        for allowed in allowed_countries:
            self.assertTrue(allowed in db_user.allowed_edit_countries)
