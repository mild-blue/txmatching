from typing import Tuple
from unittest import mock
from uuid import uuid4

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.jwt_crypto import decode_auth_token
from txmatching.auth.data_types import UserRole, EncodedBearerToken, TokenType
from txmatching.auth.exceptions import CredentialsMismatchException, InvalidIpAddressAccessException, \
    InvalidOtpException
from txmatching.auth.login_flow import credentials_login, _refresh_token, _otp_login
from txmatching.auth.service.service_crud import register_service
from txmatching.auth.user.totp import generate_otp_for_user
from txmatching.auth.user.user_crud import register_user
from txmatching.configuration.app_configuration.application_configuration import get_application_configuration
from txmatching.database.sql_alchemy_schema import AppUserModel


class Test(DbTests):
    def test_credentials_login_credentials_mismatch(self):
        usr, pwd = self._create_user()
        self.assertRaises(CredentialsMismatchException,
                          lambda: credentials_login(usr.email, pwd + 'nope'))

        self.assertRaises(CredentialsMismatchException,
                          lambda: credentials_login(usr.email + 'nope', pwd))

    def test_credentials_login_service(self):
        jwt_sec = get_application_configuration().jwt_secret
        self.assertTrue(bool(jwt_sec))
        usr, pwd = self._create_service()

        expected = EncodedBearerToken(usr.id, UserRole.SERVICE, TokenType.ACCESS)

        request = mock.MagicMock()
        request.remote_addr = usr.second_factor_material
        with mock.patch('txmatching.auth.login_flow.request', request):
            encoded = credentials_login(usr.email, pwd)
            decoded = decode_auth_token(encoded, jwt_sec)
            self.assertEqual(expected, decoded)

    def test_credentials_login_service_wrong_ip(self):
        usr, pwd = self._create_service()

        request = mock.MagicMock()
        request.remote_addr = usr.second_factor_material + '.0'
        with mock.patch('txmatching.auth.login_flow.request', request):
            self.assertRaises(InvalidIpAddressAccessException,
                              lambda: credentials_login(usr.email, pwd))

    def test_credentials_login_user(self):
        jwt_sec = get_application_configuration().jwt_secret
        self.assertTrue(bool(jwt_sec))
        usr, pwd = self._create_user()

        expected = EncodedBearerToken(usr.id, usr.role, TokenType.ACCESS)
        encoded = credentials_login(usr.email, pwd)
        decoded = decode_auth_token(encoded, jwt_sec)
        self.assertEqual(expected, decoded)

    def test_credentials_login_user_2fa(self):
        usr, pwd = self._create_user()
        expected = EncodedBearerToken(usr.id, usr.role, TokenType.OTP)

        conf = mock.MagicMock()
        conf.require_2fa = True
        conf.jwt_expiration_days = get_application_configuration().jwt_expiration_days
        conf.jwt_secret = get_application_configuration().jwt_secret

        def get_conf():
            return conf

        with mock.patch('txmatching.auth.login_flow.get_application_configuration', get_conf):
            encoded = credentials_login(usr.email, pwd)
            decoded = decode_auth_token(encoded, conf.jwt_secret)
            self.assertEqual(expected, decoded)

    def test__refresh_token(self):
        conf = get_application_configuration()
        request_token = EncodedBearerToken(1, UserRole.ADMIN, TokenType.ACCESS)
        encoded = _refresh_token(request_token, conf)
        decoded = decode_auth_token(encoded, conf.jwt_secret)

        self.assertEqual(request_token, decoded)

    def test__refresh_token_service(self):
        conf = get_application_configuration()
        request_token = EncodedBearerToken(1, UserRole.SERVICE, TokenType.ACCESS)
        self.assertRaises(AssertionError, lambda: _refresh_token(request_token, conf))

    def test__refresh_token_otp(self):
        conf = get_application_configuration()
        request_token = EncodedBearerToken(1, UserRole.ADMIN, TokenType.OTP)
        self.assertRaises(AssertionError, lambda: _refresh_token(request_token, conf))

    def test__otp_login(self):
        conf = get_application_configuration()
        usr, pwd = self._create_user()

        otp_token = EncodedBearerToken(usr.id, usr.role, TokenType.OTP)
        otp = generate_otp_for_user(usr)
        expected = EncodedBearerToken(usr.id, usr.role, TokenType.ACCESS)

        encoded = _otp_login(otp, otp_token, conf)
        decoded = decode_auth_token(encoded, conf.jwt_secret)
        self.assertEqual(expected, decoded)

    def test__otp_login_wrong_token(self):
        conf = get_application_configuration()
        usr1, _ = self._create_user()
        usr2, _ = self._create_user()

        otp_token = EncodedBearerToken(usr1.id, usr1.role, TokenType.OTP)
        wrong_otp = generate_otp_for_user(usr2)

        self.assertRaises(InvalidOtpException, lambda: _otp_login(wrong_otp, otp_token, conf))

    def _create_user(self, role: UserRole = UserRole.ADMIN) -> Tuple[AppUserModel, str]:
        pwd = str(uuid4())
        email = str(uuid4())
        register_user(email, pwd, role, '456 678 645')
        db_usr = AppUserModel.query.filter(AppUserModel.email == email).first()
        self.assertIsNotNone(db_usr)
        self.assertNotEqual(pwd, db_usr.pass_hash)
        return db_usr, pwd

    def _create_service(self) -> Tuple[AppUserModel, str]:
        pwd = str(uuid4())
        email = str(uuid4())
        register_service(email, pwd, '1.1.1.1')
        db_usr = AppUserModel.query.filter(AppUserModel.email == email).first()
        self.assertIsNotNone(db_usr)
        self.assertNotEqual(pwd, db_usr.pass_hash)
        return db_usr, pwd
