import logging

import requests

from txmatching.auth.exceptions import CouldNotSendOtpUsingSmsServiceException, require_auth_condition
from txmatching.configuration.app_configuration.application_configuration import get_application_configuration, \
    ApplicationConfiguration

logger = logging.getLogger(__name__)


def send_sms(recipient_phone: str, message_body: str):
    """
    Send SMS with message_body to recipient_phone.
    """
    app_conf = get_application_configuration()
    if app_conf.is_production:
        return _send_otp_ikem(recipient_phone, message_body, app_conf)
    else:
        raise NotImplemented('It is not possible to send SMS unless '
                             'the app is running in the production environment.')


def _send_otp_ikem(recipient_phone: str, message_body: str, app_config: ApplicationConfiguration):
    require_auth_condition(bool(app_config.sms_service_url), 'SMS service URL is not set!')
    require_auth_condition(bool(app_config.sms_service_sender), 'SMS service sender is not set!')
    require_auth_condition(bool(app_config.sms_service_login), 'SMS service login is not set!')
    require_auth_condition(bool(app_config.sms_service_password), 'SMS service password is not set!')

    params = {
        'cmd': 'send',
        'sender': app_config.sms_service_sender,
        'login': app_config.sms_service_login,
        'password': app_config.sms_service_password,
        'phone': recipient_phone,
        'message': message_body
    }
    r = requests.get(app_config.sms_service_url, params=params)
    if r.status_code != 200:
        raise CouldNotSendOtpUsingSmsServiceException(f'SMS gate responded with {r.status_code} and {r.json()}')
    else:
        logger.info('SMS sent successfully.')
