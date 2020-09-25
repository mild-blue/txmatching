from unittest import TestCase

from txmatching.auth.data_types import UserRole
from txmatching.auth.user.totp import generate_totp_seed, generate_otp_for_user, verify_otp_for_user
from txmatching.database.sql_alchemy_schema import AppUserModel


class Test(TestCase):

    def test_generate_otp_for_user(self):
        seed = generate_totp_seed()
        usr = AppUserModel('', '', UserRole.ADMIN, second_factor_material=seed)
        otp = generate_otp_for_user(usr)
        self.assertTrue(verify_otp_for_user(usr, otp))

    def test_generate_otp_for_user_service(self):
        seed = generate_totp_seed()
        usr = AppUserModel('', '', UserRole.SERVICE, second_factor_material=seed)

        self.assertRaises(AssertionError, lambda: generate_otp_for_user(usr))
