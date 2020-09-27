import datetime
from unittest import TestCase, mock
from uuid import uuid4

from txmatching.auth.data_types import UserRole, BearerTokenRequest, TokenType, EncodedBearerToken
from txmatching.auth.exceptions import InvalidOtpException, InvalidAuthCallException
from txmatching.auth.user.totp import generate_totp_seed, OTP_LIVENESS_MINUTES, generate_otp_for_user
from txmatching.auth.user.user_auth import user_login_flow, user_otp_login, refresh_user_token
from txmatching.database.sql_alchemy_schema import AppUserModel


class TestUserAuth(TestCase):

    def test_user_login_flow_service(self):
        usr = AppUserModel('', '', UserRole.SERVICE, '')
        self.assertRaises(InvalidAuthCallException, lambda: user_login_flow(usr, mock.Mock()))

    def test_user_login_flow_enabled_2fa(self):
        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone', require_2fa=True)
        usr.id = 14

        expected = BearerTokenRequest(
            user_id=usr.id,
            role=usr.role,
            type=TokenType.OTP,
            expiration=datetime.timedelta(minutes=OTP_LIVENESS_MINUTES)
        )

        token = user_login_flow(usr, 0)
        self.assertEqual(expected, token)

    def test_user_login_flow_disabled_2fa(self):
        jwt_expiration_days = 9

        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone', require_2fa=False)
        usr.id = 14

        expected = BearerTokenRequest(
            user_id=usr.id,
            role=usr.role,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(days=jwt_expiration_days)
        )

        token = user_login_flow(usr, jwt_expiration_days)
        self.assertEqual(expected, token)

    def test_user_otp_login_service(self):
        usr = AppUserModel('', '', UserRole.SERVICE, '')
        self.assertRaises(InvalidAuthCallException, lambda: user_otp_login(usr, '', mock.Mock()))

    def test_user_otp_login(self):
        jwt_expiration_days = 10

        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone')
        usr.id = 14

        expected = BearerTokenRequest(
            user_id=usr.id,
            role=usr.role,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(days=jwt_expiration_days)
        )
        valid_otp = generate_otp_for_user(usr)
        token = user_otp_login(usr, valid_otp, jwt_expiration_days)
        self.assertEqual(expected, token)

    def test_user_otp_login_wrong_otp(self):
        jwt_expiration_days = 10

        usr = AppUserModel(str(uuid4()), '', UserRole.ADMIN, generate_totp_seed(), 'phone')
        different_usr_otp = generate_otp_for_user(
            AppUserModel('', '', UserRole.ADMIN, generate_totp_seed())
        )
        self.assertRaises(InvalidOtpException, lambda: user_otp_login(usr, different_usr_otp, jwt_expiration_days))

    def test_refresh_user_token(self):
        days = 10
        expected = BearerTokenRequest(
            user_id=1,
            role=UserRole.ADMIN,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(days=days)
        )
        encoded = EncodedBearerToken(
            user_id=expected.user_id,
            role=expected.role,
            type=expected.type
        )
        refreshed = refresh_user_token(encoded, days)
        self.assertEqual(expected, refreshed)

    def test_refresh_user_token_fails_otp(self):
        encoded = EncodedBearerToken(
            user_id=1,
            role=UserRole.ADMIN,
            type=TokenType.OTP
        )
        self.assertRaises(InvalidAuthCallException, lambda: refresh_user_token(encoded, 10))

    def test_refresh_user_token_fails_service(self):
        encoded = EncodedBearerToken(
            user_id=1,
            role=UserRole.SERVICE,
            type=TokenType.ACCESS
        )
        self.assertRaises(InvalidAuthCallException, lambda: refresh_user_token(encoded, 10))
