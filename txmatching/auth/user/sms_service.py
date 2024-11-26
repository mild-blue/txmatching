import logging

import requests

from txmatching.auth.exceptions import (
    CouldNotSendOtpUsingSmsServiceException, require_auth_condition)
from txmatching.configuration.app_configuration.application_configuration import (
    ApplicationConfiguration, get_application_configuration)

logger = logging.getLogger(__name__)


def send_sms(recipient_phone: str, message_body: str):
    """
    Send SMS with message_body to recipient_phone.
    """
    return _send_otp_ikem(recipient_phone, message_body, get_application_configuration())


def _send_otp_ikem(recipient_phone: str, message_body: str, app_config: ApplicationConfiguration):
    require_auth_condition(bool(app_config.sms_service_url), 'SMS service URL is not set!')
    require_auth_condition(bool(app_config.sms_service_sender), 'SMS service sender is not set!')
    require_auth_condition(bool(app_config.sms_service_login), 'SMS service login is not set!')
    require_auth_condition(bool(app_config.sms_service_password), 'SMS service password is not set!')

    params = {
        'login': app_config.sms_service_login,
        'password': app_config.sms_service_password,
        'phone': recipient_phone,
        'message': message_body,
        'sender': app_config.sms_service_sender
    }
    try:
        # TODO: here should be something like try / except requests.Timeout / requests.ConnectionError
        #  https://github.com/mild-blue/txmatching/issues/1007
        # pylint: disable=missing-timeout
        sms_request = requests.post(app_config.sms_service_url, json=params)
        if sms_request.status_code != 200:
            raise CouldNotSendOtpUsingSmsServiceException(
                f'SMS gate responded with status code: {sms_request.status_code} '
                f'and body: {sms_request.json()}'
            )
        logger.info('SMS sent successfully.')
    except Exception as ex:
        raise CouldNotSendOtpUsingSmsServiceException('Unexpected error occurred during SMS sending.') from ex
