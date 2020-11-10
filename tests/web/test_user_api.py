import datetime
from unittest import mock
from uuid import uuid4

from tests.test_utilities.populate_db import USERS, ADMIN_USER
from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.jwt_crypto import parse_request_token, encode_auth_token
from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole, TokenType
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.configuration.app_configuration.application_configuration import get_application_configuration
from txmatching.database.db import db
from txmatching.database.services.app_user_management import persist_user, get_app_user_by_email
from txmatching.database.sql_alchemy_schema import AppUserModel


class TestUserApi(DbTests):
    def test_login_with_existing_users(self):
        for user_credentials in USERS:
            self.login_with_credentials(user_credentials)
            self.assertIsNotNone(self.auth_headers)
            auth_header = self.auth_headers['Authorization']
            self.assertTrue(auth_header.startswith('Bearer'))
            self.assertNotEqual('Bearer', auth_header)

    def test_login_should_fail(self):
        email = str(uuid4())
        password = str(uuid4())
        with self.app.test_client() as client:
            response = client.post('/user/login',
                                   json={'email': email, 'password': password})
            self.assertEqual(401, response.status_code)
            self.assertEqual('Authentication failed.', response.json['error'])

    def test_otp_login_without_header_should_fail(self):
        otp = str(uuid4())
        with self.app.test_client() as client:
            response = client.post('/user/otp',
                                   json={'otp': otp})
            self.assertEqual(401, response.status_code)
            self.assertEqual('Authentication failed.', response.json['error'])

    def test_2fa_login_with_otp_resend(self):
        password = 'hello-world'
        user = AppUserModel(
            email=str(uuid4()),
            pass_hash=encode_password(password),
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            phone_number='+420123456789',
            require_2fa=True
        )
        user = persist_user(user)
        # we must store it in self, otherwise
        # it wouldn't be possible to set it from send
        self.generated_otp = None
        self.triggered_times = 0

        def send(phone_number: str, message_body: str):
            self.assertEqual(user.phone_number, phone_number)
            token = message_body[0:6]
            self.generated_otp = token
            self.triggered_times += 1

        with mock.patch('txmatching.auth.user.user_auth.send_sms', send):
            with self.app.test_client() as client:
                response = client.post('/user/login',
                                       json={'email': user.email, 'password': password})
                self.assertEqual(200, response.status_code)
                self.assertIsNotNone(self.generated_otp)

                temp_otp_login_token = response.json['auth_token']
                decoded_token = parse_request_token(
                    auth_header=f'Bearer {temp_otp_login_token}',
                    jwt_secret=get_application_configuration().jwt_secret
                )
                self.assertEqual(TokenType.OTP, decoded_token.type)
                self.assertEqual(1, self.triggered_times)

                # test malformed token without Bearer prefix
                response = client.post('/user/otp',
                                       json={'otp': self.generated_otp},
                                       headers={'Authorization': temp_otp_login_token})
                self.assertEqual(401, response.status_code)

                # test resending token
                response = client.put('/user/otp',
                                      headers={'Authorization': f'Bearer {temp_otp_login_token}'})
                self.assertEqual(200, response.status_code)
                self.assertEqual('ok', response.json['status'])
                self.assertEqual(2, self.triggered_times)

                # try to login with correct structure and valid token
                response = client.post('/user/otp',
                                       json={'otp': self.generated_otp},
                                       headers={'Authorization': f'Bearer {temp_otp_login_token}'})
                self.assertEqual(200, response.status_code)
                login_token = response.json['auth_token']
                decoded_token = parse_request_token(
                    auth_header=f'Bearer {login_token}',
                    jwt_secret=get_application_configuration().jwt_secret
                )
                self.assertEqual(TokenType.ACCESS, decoded_token.type)

    def test_refresh_token(self):
        self.login_with_role(UserRole.ADMIN)
        with self.app.test_client() as client:
            response = client.get('/user/refresh-token',
                                  headers=self.auth_headers)
            self.assertEqual(200, response.status_code)
            self.assertIsNotNone(response.json.get('auth_token'))

    def test_refresh_token_should_fail_without_token(self):
        with self.app.test_client() as client:
            response = client.get('/user/refresh-token')
            self.assertEqual(401, response.status_code)

    def test_refresh_token_should_fail_with_otp_token(self):
        otp_bearer = encode_auth_token(
            user_id=int(ADMIN_USER['id']),
            user_role=ADMIN_USER['role'],
            token_type=TokenType.OTP,
            expiration=datetime.timedelta(hours=1),
            jwt_secret=get_application_configuration().jwt_secret
        )
        with self.app.test_client() as client:
            response = client.get('/user/refresh-token',
                                  headers={'Authorization': f'Bearer {otp_bearer}'})
            self.assertEqual(403, response.status_code)

    def test_password_change(self):
        admin_credentials = ADMIN_USER.copy()
        self.login_with_credentials(admin_credentials)
        password_change_request = {
            'current_password': admin_credentials['password'],
            'new_password': admin_credentials['password'] + str(uuid4())
        }
        with self.app.test_client() as client:
            response = client.put('/user/change-password',
                                  json=password_change_request,
                                  headers=self.auth_headers)
            self.assertEqual(200, response.status_code)

        # invalidate headers
        self.auth_headers = None
        admin_credentials['password'] = password_change_request['new_password']
        # try to login with new password
        self.login_with_credentials(admin_credentials)
        self.assertIsNotNone(self.auth_headers)

    def test_password_change_should_fail_password_mismatch(self):
        self.login_with_credentials(ADMIN_USER)
        password_change_request = {
            'current_password': str(uuid4()),
            'new_password': str(uuid4())
        }
        with self.app.test_client() as client:
            response = client.put('/user/change-password',
                                  json=password_change_request,
                                  headers=self.auth_headers)
            self.assertEqual(401, response.status_code)

    def test_register_new_user_should_fail_not_admin(self):
        self.login_with_role(UserRole.VIEWER)
        new_user = {
            'email': str(uuid4()),
            'password': str(uuid4()),
            'role': UserRole.ADMIN,
            'second_factor': '+420123456789',
            'allowed_countries': []
        }
        self.assertIsNone(get_app_user_by_email(new_user['email']))
        with self.app.test_client() as client:
            response = client.post('/user/register', json=new_user,
                                   headers=self.auth_headers)
            self.assertEqual(403, response.status_code)

        self.assertIsNone(get_app_user_by_email(new_user['email']))

    def test_register_new_user_should_fail_invalid_country(self):
        self.login_with_role(UserRole.ADMIN)
        new_user = {
            'email': str(uuid4()),
            'password': str(uuid4()),
            'role': UserRole.ADMIN,
            'second_factor': '+420123456789',
            'allowed_countries': ['MILDBLUE']
        }
        self.assertIsNone(get_app_user_by_email(new_user['email']))
        with self.app.test_client() as client:
            response = client.post('/user/register', json=new_user,
                                   headers=self.auth_headers)
            self.assertEqual(400, response.status_code)

        self.assertIsNone(get_app_user_by_email(new_user['email']))

    def test_register_new_user(self):
        self.login_with_role(UserRole.ADMIN)
        new_user = {
            'email': str(uuid4()),
            'password': str(uuid4()),
            'role': UserRole.ADMIN,
            'second_factor': '+420123456789',
            'allowed_countries': []
        }
        self.assertIsNone(get_app_user_by_email(new_user['email']))
        with self.app.test_client() as client:
            response = client.post('/user/register', json=new_user,
                                   headers=self.auth_headers)
            self.assertEqual(200, response.status_code)

        user = get_app_user_by_email(new_user['email'])
        self.assertEqual(new_user['email'], user.email)
        self.assertEqual(new_user['role'], user.role)
        self.assertEqual(new_user['second_factor'], user.phone_number)
        # check that 2fa by default is enabled
        self.assertTrue(user.require_2fa)
        # disable 2fa and try to login
        user.require_2fa = False
        db.session.commit()
        # invalidate headers
        self.auth_headers = None
        # try to log in with new user
        self.login_with(
            email=new_user['email'],
            password=new_user['password'],
            user_id=user.id,
            user_role=new_user['role']
        )
        # check set headers
        self.assertIsNotNone(self.auth_headers)
