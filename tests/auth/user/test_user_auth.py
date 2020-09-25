import datetime
from unittest import TestCase, mock
from uuid import uuid4

from txmatching.auth.data_types import UserRole, BearerTokenRequest, TokenType
from txmatching.auth.exceptions import InvalidOtpException
from txmatching.auth.user.totp import generate_totp_seed, OTP_LIVENESS_MINUTES, generate_otp_for_user
from txmatching.auth.user.user_auth import user_login_flow, user_otp_login
from txmatching.database.sql_alchemy_schema import AppUserModel


class Test(TestCase):

    def test_user_login_flow_service(self):
        usr = AppUserModel('', '', UserRole.SERVICE, '')
        self.assertRaises(AssertionError, lambda: user_login_flow(usr, mock.Mock()))

    def test_user_login_flow_enabled_2fa(self):
        conf = mock.Mock()
        conf.require_2fa = True

        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone')
        usr.id = 14

        expected = BearerTokenRequest(
            user_id=usr.id,
            role=usr.role,
            type=TokenType.OTP,
            expiration=datetime.timedelta(minutes=OTP_LIVENESS_MINUTES)
        )

        token = user_login_flow(usr, conf)
        self.assertEqual(expected, token)

    def test_user_login_flow_disabled_2fa(self):
        conf = mock.Mock()
        conf.require_2fa = False
        conf.jwt_expiration_days = 9

        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone')
        usr.id = 14

        expected = BearerTokenRequest(
            user_id=usr.id,
            role=usr.role,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(days=conf.jwt_expiration_days)
        )

        token = user_login_flow(usr, conf)
        self.assertEqual(expected, token)

    def test_user_otp_login_service(self):
        usr = AppUserModel('', '', UserRole.SERVICE, '')
        self.assertRaises(AssertionError, lambda: user_otp_login(usr, '', mock.Mock()))

    def test_user_otp_login(self):
        conf = mock.Mock()
        conf.jwt_expiration_days = 10

        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone')
        usr.id = 14

        expected = BearerTokenRequest(
            user_id=usr.id,
            role=usr.role,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(days=conf.jwt_expiration_days)
        )
        valid_otp = generate_otp_for_user(usr)
        token = user_otp_login(usr, valid_otp, conf)
        self.assertEqual(expected, token)

    def test_user_otp_login_wrong_otp(self):
        conf = mock.Mock()
        conf.jwt_expiration_days = 10

        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone')
        different_usr_otp = generate_otp_for_user(
            AppUserModel('', '', UserRole.ADMIN, generate_totp_seed())
        )
        self.assertRaises(InvalidOtpException, lambda: user_otp_login(usr, different_usr_otp, conf))
