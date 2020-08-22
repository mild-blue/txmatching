# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import request
from flask_restx import Resource, fields

from kidney_exchange.web.api.namespaces import user_api
from kidney_exchange.web.auth.login_check import login_required, require_role, get_request_token
from kidney_exchange.web.auth.user_authentication import obtain_login_token, refresh_token, register_user, \
    change_user_password

logger = logging.getLogger(__name__)


@user_api.route('/login', methods=['POST'])
class LoginApi(Resource):
    login_input_model = user_api.model('UserLogin', {
        'email': fields.String(required=True, description='Email of the user to login.'),
        'password': fields.String(required=True, description='Users password.')
    })

    @user_api.doc(body=login_input_model, responses={200: 'Success', 401: 'Auth denied'})
    def post(self):
        post_data = request.get_json()
        token, error = obtain_login_token(email=post_data.get('email'), password=post_data.get('password'))

        if error:
            return auth_denied(error)
        elif token:
            return ok_token_status(token)
        else:
            return default_inconsistency()


@user_api.route('/refresh-token', methods=['GET'])
class RefreshTokenApi(Resource):

    @user_api.doc(security='bearer', responses={200: 'Success', 401: 'Auth denied'})
    @login_required()
    def get(self):
        error, token = None, None
        try:
            # should always succeed as [login_required] annotation is used
            auth_token = request.headers.get('Authorization').split(" ")[1]
            token, error = refresh_token(auth_token)
        # pylint: disable=broad-except
        # as this is authentication, we need to catch everything
        except Exception:
            error = 'Bearer token malformed.'

        if error:
            return auth_denied(error)
        elif token:
            return ok_token_status(token)
        else:
            return default_inconsistency()


@user_api.route('/change-password', methods=['PUT'])
class PasswordChangeApi(Resource):
    password_change_model = user_api.model('PasswordChange', {
        'new_password': fields.String(required=True, description='New password.')
    })

    @user_api.doc(body=password_change_model, security='bearer')
    @login_required()
    def put(self):
        data = request.get_json()
        token = get_request_token()
        if token:
            change_user_password(email=token.user_email, new_password=data.get('new_password'))
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
    @require_role('ADMIN')
    def post(self):
        post_data = request.get_json()
        token, error = register_user(email=post_data.get('email'),
                                     password=post_data.get('password'),
                                     role=post_data.get('role'))
        if error:
            return {'status': 'error', 'message': error}, 400
        elif token:
            return ok_token_status(token)
        else:
            return default_inconsistency()


def ok_token_status(token: str):
    return {'status': 'ok', 'auth_token': token}


def auth_denied(error: str):
    return {'status': 'error', 'message': error}, 401


def default_inconsistency():
    return {'status': 'error', 'message': 'Internal inconsistency.'}, 500
