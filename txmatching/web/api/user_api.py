# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class
import logging
from typing import Tuple

from flask import request
from flask_restx import Resource, fields

from txmatching.auth.auth_check import require_role
from txmatching.auth.auth_management import change_password, register
from txmatching.auth.data_types import UserRole
from txmatching.auth.login_flow import (credentials_login, otp_login,
                                        refresh_token)
from txmatching.auth.user.topt_auth_check import allow_otp_request
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    FailJson
from txmatching.web.api.namespaces import user_api

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

    @user_api.doc(body=login_input_model)
    @user_api.response(code=200, model=LoginSuccessResponse,
                       description='Login successful. JWT generated. User must attach the token to every request '
                                   'in the "Authorization" header with the prefix "Bearer". Example: '
                                   '"Authorization: Bearer some_token", where some_token is the token received '
                                   'in the response.')
    @user_api.response(code=400, model=FailJson, description='Wrong data format.')
    @user_api.response(code=401, model=FailJson, description='Authentication denied.')
    @user_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    def post(self):
        post_data = request.get_json()
        auth_response = credentials_login(email=post_data.get('email'), password=post_data.get('password'))
        return _respond_token(auth_response)


@user_api.route('/otp', methods=['POST'])
class OtpLoginApi(Resource):
    otp_input_model = user_api.model('OtpLogin', {
        'otp': fields.String(required=True, description='OTP for this login.'),
    })

    @user_api.doc(security='bearer')
    @user_api.doc(body=otp_input_model)
    @user_api.response(code=200, model=LoginSuccessResponse,
                       description='OTP validation was successful. JWT generated.')
    @user_api.response(code=400, model=FailJson, description='Wrong data format.')
    @user_api.response(code=401, model=FailJson, description='Authentication denied.')
    @user_api.response(
        code=403,
        model=FailJson,
        description='Access denied. You do not have rights to access this endpoint.'
    )
    @user_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @allow_otp_request()
    def post(self):
        post_data = request.get_json()
        auth_response = otp_login(post_data.get('otp'))
        return _respond_token(auth_response)


@user_api.route('/refresh-token', methods=['GET'])
class RefreshTokenApi(Resource):

    @user_api.doc(security='bearer')
    @user_api.response(code=200, model=LoginSuccessResponse, description='Token successfully refreshed.')
    @user_api.response(code=400, model=FailJson, description='Wrong data format.')
    @user_api.response(code=401, model=FailJson, description='Authentication denied.')
    @user_api.response(
        code=403,
        model=FailJson,
        description='Access denied. You do not have rights to access this endpoint.'
    )
    @user_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def get(self):
        return _respond_token(refresh_token())


@user_api.route('/change-password', methods=['PUT'])
class PasswordChangeApi(Resource):
    input = user_api.model('PasswordChange', {
        'new_password': fields.String(required=True, description='New password.')
    })

    @user_api.doc(body=input, security='bearer')
    @user_api.response(code=200, model=StatusResponse, description='Password changed successfully.')
    @user_api.response(code=400, model=FailJson, description='Wrong data format.')
    @user_api.response(code=401, model=FailJson, description='Authentication denied.')
    @user_api.response(
        code=403,
        model=FailJson,
        description='Access denied. You do not have rights to access this endpoint.'
    )
    @user_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def put(self):
        data = request.get_json()
        change_password(new_password=data.get('new_password'))
        return {'status': 'ok'}, 200


@user_api.route('/register', methods=['POST'])
class RegistrationApi(Resource):
    registration_model = user_api.model('UserRegistration', dict(
        email=fields.String(required=True, description='Email/username used for authentication.'),
        password=fields.String(required=True, description='User\'s password.'),
        role=fields.String(required=True, enum=[role.name for role in UserRole], description='User\'s role.'),
        second_factor=fields.String(required=True,
                                    description='2FA: Phone number for user account, IP address for SERVICE account.')))

    @user_api.doc(body=registration_model, security='bearer')
    @user_api.response(code=200, model=StatusResponse, description='User registered successfully.')
    @user_api.response(code=400, model=FailJson, description='Wrong data format.')
    @user_api.response(code=401, model=FailJson, description='Authentication denied.')
    @user_api.response(
        code=403,
        model=FailJson,
        description='Access denied. You do not have rights to access this endpoint.'
    )
    @user_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_role(UserRole.ADMIN)
    def post(self):
        post_data = request.get_json()
        register(email=post_data.get('email'),
                 password=post_data.get('password'),
                 role=UserRole(post_data.get('role')),
                 second_factor=post_data.get('second_factor'))
        return {'status': 'ok'}, 200


def _respond_token(token: str) -> Tuple[dict, int]:
    return {'auth_token': token}, 200
