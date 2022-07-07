# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging
import requests

from flask import request
from flask_restx import Resource, fields

from txmatching.auth.auth_check import require_role
from txmatching.auth.auth_management import (change_password, get_reset_token,
                                             get_user_id_for_email, register,
                                             reset_password)
from txmatching.auth.data_types import UserRole
from txmatching.auth.login_flow import (credentials_login, otp_login,
                                        refresh_token, resend_otp)
from txmatching.auth.user.topt_auth_check import allow_otp_request
from txmatching.data_transfer_objects.shared_dto import SuccessDTOOut
from txmatching.data_transfer_objects.shared_swagger import SuccessJsonOut
from txmatching.data_transfer_objects.users.user_dto import (
    UserRegistrationDtoIn, UserRegistrationDtoOut)
from txmatching.data_transfer_objects.users.user_swagger import (
    LoginInputJson, LoginSuccessJson, OtpInJson, PasswordChangeInJson,
    RegistrationJson, RegistrationOutJson, ResetRequestJson)
from txmatching.web.web_utils.namespaces import user_api
from txmatching.web.web_utils.route_utils import request_body, response_ok, response_bad_request

logger = logging.getLogger(__name__)


@user_api.route('/login', methods=['POST'])
class LoginApi(Resource):

    @user_api.request_body(LoginInputJson,
                           description='Endpoint to be used for login of users. Returns JWT. This JWT serves two'
                                       ' purposes: in the case of '
                                       'normal accounts it can be used to obtain OTP at the /otp endpoint; in the case '
                                       'of service accounts it can be directly used to access '
                                       '/public/patient-upload endpoint')
    @user_api.response_ok(LoginSuccessJson,
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

    @user_api.doc(security='bearer')
    @user_api.request_body(OtpInJson)
    @user_api.response_ok(LoginSuccessJson, 'OTP validation was successful. JWT generated.')
    @user_api.response_errors()
    @user_api.response_error_sms_gate()
    @allow_otp_request()
    def post(self):
        post_data = request.get_json()
        auth_response = otp_login(post_data.get('otp'))
        return response_ok(_respond_token(auth_response))

    @user_api.doc(security='bearer')
    @user_api.response_ok(SuccessJsonOut, description='Whether the new OTP was generated and sent.')
    @user_api.response_errors()
    @user_api.response_error_sms_gate()
    @allow_otp_request()
    def put(self):
        resend_otp()
        return response_ok(SuccessDTOOut(success=True))


@user_api.route('/refresh-tokenl', methods=['GET'])
class RefreshTokenApi(Resource):

    @user_api.require_user_login()
    @user_api.response_ok(LoginSuccessJson, description='Token successfully refreshed.')
    @user_api.response_errors()
    def get(self):
        return response_ok(_respond_token(refresh_token()))


@user_api.route('/change-password', methods=['PUT'])
class PasswordChangeApi(Resource):

    @user_api.require_user_login()
    @user_api.request_body(PasswordChangeInJson)
    @user_api.response_ok(SuccessJsonOut, description='Whether the password was changed successfully.')
    @user_api.response_errors()
    def put(self):
        data = request.get_json()
        change_password(current_password=data['current_password'], new_password=data['new_password'])
        return response_ok(SuccessDTOOut(success=True))


@user_api.route('/<email>/reset-password-token', methods=['GET'])
class RequestReset(Resource):

    @user_api.require_user_login()
    @user_api.response_ok(ResetRequestJson, description='Returns reset token.')
    @user_api.response_errors()
    @require_role(UserRole.ADMIN)
    def get(self, email: str):
        reset_token = get_reset_token(get_user_id_for_email(email))
        return response_ok({'token': reset_token})


@user_api.route('/reset-password', methods=['PUT'])
class ResetPassword(Resource):
    reset_password_input = user_api.model('ResetPassword', {
        'token': fields.String(required=True, description='Reset Token.'),
        'password': fields.String(required=True, description='New password.')
    })

    @user_api.request_body(reset_password_input)
    @user_api.response_ok(SuccessJsonOut, description='Whether the password reset was successful.')
    @user_api.response_errors()
    def put(self):
        body = request.get_json()

        # This is for testing purposes only. It emulates success response but do not change anything.
        if body['token'] == 'mock-success':
            return response_ok(SuccessDTOOut(success=True))

        reset_password(body['token'], body['password'])
        return response_ok(SuccessDTOOut(success=True))


@user_api.route('/register', methods=['POST'])
class RegistrationApi(Resource):

    @user_api.require_user_login()
    @user_api.request_body(RegistrationJson)
    @user_api.response_ok(RegistrationOutJson, description='Detailed info about the registered user.')
    @user_api.response_errors()
    @require_role(UserRole.ADMIN)
    def post(self):
        registration_dto = request_body(UserRegistrationDtoIn)
        token = register(registration_dto)
        password_reset_token_message = f'To reset password for the new user with email {registration_dto.email} go to:' \
                                       f'{request.url_root}/#/reset-password/{token}'
        return response_ok(UserRegistrationDtoOut(
            role=registration_dto.role,
            email=registration_dto.email,
            password_reset_token_message=password_reset_token_message,
            password_reset_token=token,
            allowed_countries=registration_dto.allowed_countries,
            allowed_txm_events=registration_dto.allowed_txm_events
        )
        )


def _respond_token(token: str) -> dict:
    return {'auth_token': token}


@user_api.route('/authentik-login', methods=['GET'])
class AuthentikLogin(Resource):
    def get(self):
        code = request.args.get('code')
        if code is None:
            return response_bad_request({'error': 'No code provided'})

        data = {
            "client_id": "f5c6b6a72ff4f7bbdde383a26bdac192b2200707",
            "client_secret": "37e841e70b842a0d1237b3f7753b5d7461307562568b5add7edcfa6630d578fdffb7ff4d5c0f845d10f8f82bc1d80cec62cb397fd48795a5b1bee6090e0fa409",
            "code": code,
            "redirect_uri": "http://localhost:8080/v1/user/authentik-login",
            "grant_type": "authorization_code"
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        authentik_res = requests.post('http://host.docker.internal:9000/application/o/token/', data=data, headers=headers)
        authentik_res = authentik_res.json()

        response = response_ok(authentik_res)
        response.set_cookie("access_token", value=authentik_res["access_token"])
        response.set_cookie("refresh_token", value=authentik_res["refresh_token"])
        return response
