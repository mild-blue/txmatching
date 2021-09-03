import datetime
import random
from unittest import TestCase, mock
from uuid import uuid4

from txmatching.auth.data_types import (BearerTokenRequest, DecodedBearerToken,
                                        TokenType, UserRole)
from txmatching.auth.exceptions import (InvalidAuthCallException,
                                        InvalidOtpException)
from txmatching.auth.user.totp import (generate_otp_for_user,
                                       generate_totp_seed, verify_otp_for_user)
from txmatching.auth.user.user_auth import (
    JWT_FOR_OTP_ACQUISITION_VALIDITY_MINUTES, _send_sms_otp,
    refresh_user_token, user_login_flow, user_otp_login)
from txmatching.database.sql_alchemy_schema import AppUserModel


class TestUserAuth(TestCase):

    def test_user_login_flow_service(self):
        usr = AppUserModel(email='', pass_hash='', role=UserRole.SERVICE, second_factor_material='')
        self.assertRaises(InvalidAuthCallException, lambda: user_login_flow(usr, mock.Mock()))

    def test_user_login_flow_enabled_2fa(self):
        usr = AppUserModel(
            email=str(uuid4()),
            pass_hash='',
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            phone_number='phone',
            require_2fa=True
        )
        usr.id = 14

        expected = BearerTokenRequest(
            user_id=usr.id,
            role=usr.role,
            type=TokenType.OTP,
            expiration=datetime.timedelta(minutes=JWT_FOR_OTP_ACQUISITION_VALIDITY_MINUTES)
        )

        def send_sms_mock(phone_number: str, message_body: str):
            self.assertEqual(usr.phone_number, phone_number)
            token = message_body[0:6]
            self.assertTrue(verify_otp_for_user(usr, token))

        with mock.patch('txmatching.auth.user.user_auth.send_sms', send_sms_mock):
            token = user_login_flow(usr, 0)
            self.assertEqual(expected, token)

    def test_user_login_flow_disabled_2fa(self):
        jwt_expiration_days = 9

        usr = AppUserModel(
            email=str(uuid4()),
            pass_hash='',
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            phone_number='',
            require_2fa=False
        )
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
        usr = AppUserModel(email='', pass_hash='', role=UserRole.SERVICE, second_factor_material='')
        self.assertRaises(InvalidAuthCallException, lambda: user_otp_login(usr, '', mock.Mock()))

    def test_user_otp_login(self):
        jwt_expiration_days = 10

        usr = AppUserModel(
            email=str(uuid4()),
            pass_hash='',
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            phone_number='phone'
        )
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

        usr = AppUserModel(
            email=str(uuid4()),
            pass_hash='',
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            phone_number='phone'
        )
        different_usr_otp = generate_otp_for_user(
            AppUserModel(
                email='',
                pass_hash='',
                role=UserRole.ADMIN,
                second_factor_material=generate_totp_seed()
            )
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
        encoded = DecodedBearerToken(
            user_id=expected.user_id,
            role=expected.role,
            type=expected.type
        )
        refreshed = refresh_user_token(encoded, days)
        self.assertEqual(expected, refreshed)

    def test_refresh_user_token_fails_otp(self):
        encoded = DecodedBearerToken(
            user_id=1,
            role=UserRole.ADMIN,
            type=TokenType.OTP
        )
        self.assertRaises(InvalidAuthCallException, lambda: refresh_user_token(encoded, 10))

    def test_refresh_user_token_fails_service(self):
        encoded = DecodedBearerToken(
            user_id=1,
            role=UserRole.SERVICE,
            type=TokenType.ACCESS
        )
        self.assertRaises(InvalidAuthCallException, lambda: refresh_user_token(encoded, 10))

    def test__send_sms_otp(self):
        usr = mock.MagicMock()
        usr.phone_number = 'phone'

        token = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        def send_sms_mock(phone_number: str, message_body: str):
            self.assertEqual(usr.phone_number, phone_number)
            self.assertEqual(f'{token} - use this code for TXMatching login.', message_body)

        with mock.patch('txmatching.auth.user.user_auth.send_sms', send_sms_mock):
            _send_sms_otp(token, usr)
