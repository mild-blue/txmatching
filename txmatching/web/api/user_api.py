# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import jsonify, request
from flask_restx import Resource, fields

from txmatching.auth.data_types import (BearerToken, FailResponse,
                                        LoginSuccessResponse, UserRole)
from txmatching.auth.login_check import (get_request_token, login_required,
                                         require_role)
from txmatching.auth.user_authentication import (change_user_password,
                                                 obtain_login_token,
                                                 refresh_token, register_user)
from txmatching.web.api.namespaces import user_api

logger = logging.getLogger(__name__)

LOGIN_SUCCESS_RESPONSE = user_api.model('LoginSuccessResponse', {
    'auth_token': fields.String(required=True),
})

LOGIN_FAIL_RESPONSE = user_api.model('LoginFailResponse', {
    'error': fields.String(required=True),
})


@user_api.route('/login', methods=['POST'])
class LoginApi(Resource):
    login_input_model = user_api.model('UserLogin', {
        'email': fields.String(required=True, description='Email of the user to login.'),
        'password': fields.String(required=True, description='Users password.')
    })

    @user_api.doc(body=login_input_model)
    @user_api.response(code=200, model=LOGIN_SUCCESS_RESPONSE, description='')
    @user_api.response(code=401, model=LOGIN_FAIL_RESPONSE, description='')
    def post(self):
        post_data = request.get_json()
        maybe_token = obtain_login_token(email=post_data.get('email'), password=post_data.get('password'))

        if isinstance(maybe_token, LoginSuccessResponse):
            return jsonify(maybe_token)
        return jsonify(maybe_token), 401


@user_api.route('/refresh-token', methods=['GET'])
class RefreshTokenApi(Resource):

    @user_api.doc(security='bearer')
    @user_api.response(code=200, model=LOGIN_SUCCESS_RESPONSE, description='')
    @user_api.response(code=401, model=LOGIN_FAIL_RESPONSE, description='')
    @login_required()
    def get(self):
        try:
            # should always succeed as [login_required] annotation is used
            auth_token = request.headers.get('Authorization').split(' ')[1]
            maybe_token = refresh_token(auth_token)
        # pylint: disable=broad-except
        # as this is authentication, we need to catch everything
        except Exception:
            maybe_token = FailResponse('Bearer token malformed.')

        if isinstance(maybe_token, LoginSuccessResponse):
            return jsonify(maybe_token)
        return jsonify(maybe_token), 401


@user_api.route('/change-password', methods=['PUT'])
class PasswordChangeApi(Resource):
    password_change_model = user_api.model('PasswordChange', {
        'new_password': fields.String(required=True, description='New password.')
    })

    @user_api.doc(body=password_change_model, security='bearer', responses={400: {'status': 'error'},
                                                                            200: {'status': 'ok'}})
    @login_required()
    def put(self):
        data = request.get_json()
        token = get_request_token()
        if isinstance(token, BearerToken):
            change_user_password(user_id=token.user_id, new_password=data.get('new_password'))
            return {'status': 'ok'}
        else:
            return {'status': 'error'}, 400


@user_api.route('/register', methods=['POST'])
class RegistrationApi(Resource):
    registration_model = user_api.model('UserRegistration', {
        'email': fields.String(required=True, description='Email used for authentication.'),
        'password': fields.String(required=True, description='Users password.'),
        'role': fields.String(required=True, description='Users role.'),
    })

    @user_api.doc(body=registration_model, security='bearer')
    @user_api.response(code=200, model=LOGIN_SUCCESS_RESPONSE, description='')
    @user_api.response(code=400, model=LOGIN_FAIL_RESPONSE, description='')
    @require_role(UserRole.ADMIN)
    def post(self):
        post_data = request.get_json()
        login_response = register_user(email=post_data.get('email'),
                                       password=post_data.get('password'),
                                       role=post_data.get('role'))
        if isinstance(login_response, LoginSuccessResponse):
            return jsonify(login_response)
        return jsonify(login_response), 401
