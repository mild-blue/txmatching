from unittest import mock

from dacite import DaciteError
from werkzeug.exceptions import HTTPException

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.exceptions import (CredentialsMismatchException,
                                        InvalidArgumentException,
                                        InvalidAuthCallException,
                                        InvalidIpAddressAccessException,
                                        InvalidJWTException,
                                        InvalidOtpException,
                                        UserUpdateException)
from txmatching.web import USER_NAMESPACE, user_api


class TestErrorHandler(DbTests):

    def test_handle_invalid_jwt_exception(self):
        self.auth_headers = {'Authorization': f'Bearer invalid_token'}
        self._test_handler(
            side_effect=InvalidJWTException,
            status_code=401,
            error='Authentication failed.',
            detail='Invalid JWT.',
            message=''
        )

    def test_handle_credentials_mismatch_exception(self):
        self._test_handler(
            side_effect=CredentialsMismatchException,
            status_code=401,
            error='Authentication failed.',
            detail='Credentials mismatch.',
            message=''
        )

    def test_handle_invalid_otp_exception(self):
        self._test_handler(
            side_effect=InvalidOtpException,
            status_code=401,
            error='Authentication failed.',
            detail='Invalid OTP.',
            message=''
        )

    def test_handle_invalid_ip_exception(self):
        self._test_handler(
            side_effect=InvalidIpAddressAccessException,
            status_code=401,
            error='Authentication failed.',
            detail='Used IP is not whitelisted.',
            message=''
        )

    def test_handle_user_update_exception(self):
        self._test_handler(
            side_effect=UserUpdateException,
            status_code=400,
            error='Invalid data submitted.',
            detail='',
            message=''
        )

    def test_handle_invalid_auth_call_exception(self):
        self._test_handler(
            side_effect=InvalidAuthCallException,
            status_code=500,
            error='Internal error, please contact support.',
            detail='',
            message=''
        )

    def test_handle_invalid_argument_exception(self):
        self._test_handler(
            side_effect=InvalidArgumentException,
            status_code=400,
            error='Invalid argument.',
            detail='',
            message=''
        )

    def test_handle_dacite_exception(self):
        self._test_handler(
            side_effect=DaciteError,
            status_code=400,
            error='Invalid request data.',
            detail='',
            message=''
        )

    def test_handle_invalid_value_error(self):
        self._test_handler(
            side_effect=ValueError,
            status_code=400,
            error='Invalid argument.',
            detail='',
            message=''
        )

    def test_handle_http_exception(self):
        self._test_handler(
            side_effect=HTTPException,
            status_code=500,
            error='Unknown Error',
            detail=None,
            message='??? Unknown Error: None'
        )

    def test_handle_default_exception_error(self):
        self._test_handler(
            side_effect=Exception,
            status_code=500,
            error='Internal server error',
            detail='',
            message=''
        )

    def _test_handler(
            self,
            side_effect: any,
            status_code: int,
            error: str,
            detail: str,
            message: str,
            content_type: str = 'application/json'
    ):
        self.api.add_namespace(user_api, path=f'/{USER_NAMESPACE}')
        with mock.patch('txmatching.web.api.user_api.LoginApi.post') as api_mock:
            api_mock.side_effect = side_effect()
            with self.app.test_client() as client:
                res = client.post(
                    f'/{USER_NAMESPACE}/login',
                    headers=self.auth_headers,
                    json={'email': 'admin@mild.blue', 'password': 'admin'}
                )
                self.assertEqual(status_code, res.status_code)
                self.assertEqual(content_type, res.content_type)
                self.assertIsNotNone(res.json)
                self.assertEqual(error, res.json['error'])
                self.assertEqual(detail, res.json['detail'])
                self.assertEqual(message, res.json['message'])
