from flask_restx import fields

from txmatching.auth.data_types import UserRole
from txmatching.data_transfer_objects.enums_swagger import CountryCodeJson
from txmatching.web.web_utils.namespaces import user_api

LoginInputJson = user_api.model('UserLogin', {
    'email': fields.String(required=True, description='Email of the user to login.'),
    'password': fields.String(required=True, description='User\'s password.')
})

OtpInJson = user_api.model('OtpLogin', {
    'otp': fields.String(required=True, description='OTP for this login.'),
})

PasswordChangeInJson = user_api.model('PasswordChange', {
    'current_password': fields.String(required=True, description='Current password.'),
    'new_password': fields.String(required=True, description='New password.')
})

RegistrationJson = user_api.model('UserRegistration', dict(
    email=fields.String(required=True, description='Email/username used for authentication.'),
    password=fields.String(required=True, description='User\'s password.'),
    role=fields.String(required=True, enum=[role.name for role in UserRole], description='User\'s role.'),
    require_second_factor=fields.Boolean(required=True, example=True,
                                         description='Whether to require second factor for the user'),
    second_factor=fields.String(required=True,
                                description='2FA: Phone number for user account in standard format (see example), '
                                            'IP address for SERVICE account.',
                                example='+420657123987'),
    allowed_countries=fields.List(required=True,
                                  description='Countries that the user has access to.',
                                  cls_or_instance=fields.Nested(CountryCodeJson),
                                  example=['AUT', 'CZE']),
    allowed_txm_events=fields.List(required=True,
                                   description='Countries that the user has access to.',
                                   cls_or_instance=fields.String(required=True, description='Name of TXM event'),
                                   example=['test'])
))

LoginSuccessJson = user_api.model('LoginSuccessResponse', {
    'auth_token': fields.String(required=True),
})

ResetRequestJson = user_api.model('ResetRequestResponse', {
    'token': fields.String(required=True)
})

RegistrationOutJson = user_api.model('UserRegistrationOut', dict(
    email=fields.String(required=True, description='Email/username used for authentication.'),
    role=fields.String(required=True, enum=[role.name for role in UserRole], description='User\'s role.'),
    allowed_countries=fields.List(required=True,
                                  description='Countries that the user has access to.',
                                  cls_or_instance=fields.Nested(CountryCodeJson),
                                  example=['AUT', 'CZE']),
    allowed_txm_events=fields.List(required=True,
                                   description='Countries that the user has access to.',
                                   cls_or_instance=fields.String(required=True, description='Name of TXM event'),
                                   example=['test']),
    password_reset_token=fields.String(required=True,
                                       description='token to reset password',
                                       example='long_string_token'),
    password_reset_token_message=fields.String(required=True,
                                               description='detailed description how to reset password including url',
                                               example='To reset password go tu url: www.reset.password/token'),
))
