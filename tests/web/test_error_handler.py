from unittest import mock

from dacite import DaciteError
from werkzeug.exceptions import HTTPException

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.exceptions import (CredentialsMismatchException,
                                        GuardException,
                                        InvalidArgumentException,
                                        InvalidAuthCallException,
                                        InvalidIpAddressAccessException,
                                        InvalidJWTException,
                                        InvalidOtpException,
                                        UserUpdateException)
from txmatching.web import API_VERSION, USER_NAMESPACE


class TestErrorHandler(DbTests):

    def test_handle_invalid_jwt_exception(self):
        self.auth_headers = {'Authorization': f'Bearer invalid_token'}
        self._test_handler(
            side_effect=InvalidJWTException,
            status_code=401,
            error='Authentication failed.',
            message='Invalid JWT.'
        )

    def test_handle_credentials_mismatch_exception(self):
        self._test_handler(
            side_effect=CredentialsMismatchException,
            status_code=401,
            error='Authentication failed.',
            message='Credentials mismatch.'
        )

    def test_handle_invalid_otp_exception(self):
        self._test_handler(
            side_effect=InvalidOtpException,
            status_code=401,
            error='Authentication failed.',
            message='Invalid OTP.'
        )

    def test_handle_invalid_ip_exception(self):
        self._test_handler(
            side_effect=InvalidIpAddressAccessException,
            status_code=401,
            error='Authentication failed.',
            message='Used IP is not whitelisted.'
        )

    def test_handle_user_update_exception(self):
        self._test_handler(
            side_effect=UserUpdateException,
            status_code=400,
            error='Invalid data submitted.',
            message=''
        )

    def test_handle_invalid_auth_call_exception(self):
        self._test_handler(
            side_effect=InvalidAuthCallException,
            status_code=500,
            error='Internal error, please contact support.',
            message=''
        )

    def test_handle_guard_exception(self):
        self._test_handler(
            side_effect=GuardException,
            status_code=403,
            error='Access denied.',
            message=''
        )

    def test_handle_invalid_argument_exception(self):
        self._test_handler(
            side_effect=InvalidArgumentException,
            status_code=400,
            error='Invalid argument.',
            message=''
        )

    def test_handle_dacite_exception(self):
        self._test_handler(
            side_effect=DaciteError,
            status_code=400,
            error='Invalid request data.',
            message=''
        )

    def test_handle_key_error(self):
        self._test_handler(
            side_effect=KeyError,
            status_code=400,
            error='Invalid request data.',
            message=''
        )

    def test_handle_invalid_value_error(self):
        self._test_handler(
            side_effect=ValueError,
            status_code=400,
            error='Invalid request data.',
            message=''
        )

    def test_handle_http_exception(self):
        # noinspection PyTypeChecker
        # we submit detail=None on purpose
        self._test_handler(
            side_effect=HTTPException,
            status_code=500,
            error='Unknown Error',
            message='??? Unknown Error: None'
        )

    def test_handle_default_exception_error(self):
        self._test_handler(
            side_effect=Exception,
            status_code=500,
            error='Internal server error',
            message=''
        )

    def _test_handler(
            self,
            side_effect: any,
            status_code: int,
            error: str,
            message: str,
            content_type: str = 'application/json'
    ):
        with mock.patch('txmatching.web.api.user_api.LoginApi.post') as api_mock:
            api_mock.side_effect = side_effect()
            with self.app.test_client() as client:
                res = client.post(
                    f'{API_VERSION}/{USER_NAMESPACE}/login',
                    headers=self.auth_headers,
                    json={'email': 'admin@mild.blue', 'password': 'admin'}
                )
                self.assertEqual(status_code, res.status_code)
                self.assertEqual(content_type, res.content_type)
                self.assertIsNotNone(res.json)
                self.assertEqual(error, res.json['error'])
                self.assertEqual(message, res.json['message'])
