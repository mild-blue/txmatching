import logging

from flask import request, jsonify, make_response
from flask_restx import Namespace, Resource, fields

from kidney_exchange.web.auth.user_authentication import obtain_login_token, refresh_token

logger = logging.getLogger(__name__)

user_api = Namespace('user')


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


@user_api.route('/refresh-token', methods=['GET'])
class RefreshTokenApi(Resource):
    @user_api.doc(security='bearer', responses={200: 'Success', 401: 'Auth denied'})
    def get(self):
        auth_header = request.headers.get('Authorization')
        error, token = None, None
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
                token, token_error = refresh_token(auth_token)
                error = token_error
            except Exception:
                error = 'Bearer token malformed.'
        else:
            error = 'Access denied.'

        if error:
            return auth_denied(error)
        elif token:
            return ok_token_status(token)


def ok_token_status(token: str) -> str:
    return jsonify({'status': 'ok', 'auth_token': token})


def auth_denied(error: str):
    return make_response(jsonify({'status': 'error', 'message': error}), 401)
