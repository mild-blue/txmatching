# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging

from flask import request
from flask_restx import Resource, fields

from txmatching.auth.auth_check import require_role
from txmatching.auth.auth_management import change_password, register
from txmatching.auth.data_types import UserRole
from txmatching.auth.login_flow import (credentials_login, otp_login,
                                        refresh_token, resend_otp)
from txmatching.auth.user.topt_auth_check import allow_otp_request
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.enums_swagger import CountryCodeJson
from txmatching.utils.country_enum import Country
from txmatching.web.web_utils.namespaces import user_api
from txmatching.web.web_utils.route_utils import response_ok

logger = logging.getLogger(__name__)

LoginSuccessResponse = user_api.model('LoginSuccessResponse', {
    'auth_token': fields.String(required=True),
})

StatusResponse = user_api.model('StatusResponse', {
    'status': fields.String(required=True)
})


@user_api.route('/login', methods=['POST'])
class LoginApi(Resource):
    login_input_model = user_api.model('UserLogin', {
        'email': fields.String(required=True, description='Email of the user to login.'),
        'password': fields.String(required=True, description='User\'s password.')
    })

    @user_api.request_body(login_input_model)
    @user_api.response_ok(LoginSuccessResponse,
                          description='Login successful. JWT generated. User must attach the token to every request '
                                      'in the "Authorization" header with the prefix "Bearer". Example: '
                                      '"Authorization: Bearer some_token", where some_token is the token received '
                                      'in the response.')
    @user_api.response_errors()
    def post(self):
        post_data = request.get_json()
        auth_response = credentials_login(email=post_data['email'], password=post_data['password'])
        return response_ok(_respond_token(auth_response))


@user_api.route('/otp', methods=['POST', 'PUT'])
class OtpLoginApi(Resource):
    otp_input_model = user_api.model('OtpLogin', {
        'otp': fields.String(required=True, description='OTP for this login.'),
    })

    @user_api.doc(security='bearer')
    @user_api.request_body(otp_input_model)
    @user_api.response_ok(LoginSuccessResponse, 'OTP validation was successful. JWT generated.')
    @user_api.response_errors()
    @user_api.response_error_sms_gate()
    @allow_otp_request()
    def post(self):
        post_data = request.get_json()
        auth_response = otp_login(post_data.get('otp'))
        return response_ok(_respond_token(auth_response))

    @user_api.doc(security='bearer')
    @user_api.response_ok(StatusResponse, description='New OTP was generated and sent.')
    @user_api.response_errors()
    @user_api.response_error_sms_gate()
    @allow_otp_request()
    def put(self):
        resend_otp()
        return response_ok({'status': 'ok'})


@user_api.route('/refresh-token', methods=['GET'])
class RefreshTokenApi(Resource):

    @user_api.require_user_login()
    @user_api.response_ok(LoginSuccessResponse, description='Token successfully refreshed.')
    @user_api.response_errors()
    def get(self):
        return response_ok(_respond_token(refresh_token()))


@user_api.route('/change-password', methods=['PUT'])
class PasswordChangeApi(Resource):
    input = user_api.model('PasswordChange', {
        'current_password': fields.String(required=True, description='Current password.'),
        'new_password': fields.String(required=True, description='New password.')
    })

    @user_api.require_user_login()
    @user_api.request_body(input)
    @user_api.response_ok(StatusResponse, description='Password changed successfully.')
    @user_api.response_errors()
    def put(self):
        data = request.get_json()
        change_password(current_password=data['current_password'], new_password=data['new_password'])
        return response_ok({'status': 'ok'})


@user_api.route('/register', methods=['POST'])
class RegistrationApi(Resource):
    registration_model = user_api.model('UserRegistration', dict(
        email=fields.String(required=True, description='Email/username used for authentication.'),
        password=fields.String(required=True, description='User\'s password.'),
        role=fields.String(required=True, enum=[role.name for role in UserRole], description='User\'s role.'),
        second_factor=fields.String(required=True,
                                    description='2FA: Phone number for user account in standard format (see example), '
                                                'IP address for SERVICE account.',
                                    example='+420657123987'),
        allowed_countries=fields.List(required=True,
                                      description='Countries that the user has access to.',
                                      cls_or_instance=fields.Nested(CountryCodeJson),
                                      example=['AUT', 'CZE']),
    ))

    @user_api.require_user_login()
    @user_api.request_body(registration_model)
    @user_api.response_ok(StatusResponse, description='User registered successfully.')
    @user_api.response_errors()
    @require_role(UserRole.ADMIN)
    def post(self):
        post_data = request.get_json()
        register(email=post_data['email'],
                 password=post_data['password'],
                 role=UserRole(post_data['role']),
                 second_factor=post_data['second_factor'],
                 allowed_countries=[Country(country_value) for country_value in post_data['allowed_countries']])
        return response_ok({'status': 'ok'})


def _respond_token(token: str) -> dict:
    return {'auth_token': token}
