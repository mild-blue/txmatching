from unittest import TestCase, mock

import responses
from responses.matchers import json_params_matcher

from txmatching.auth.exceptions import CouldNotSendOtpUsingSmsServiceException
from txmatching.auth.user.sms_service import _send_otp_ikem


class TestSmsService(TestCase):
    @responses.activate
    def test__send_sms(self):
        app_config = mock.MagicMock()
        app_config.sms_service_url = 'https://some.domain/SendSms'
        app_config.sms_service_sender = 'sender1'
        app_config.sms_service_login = 'test'
        app_config.sms_service_password = 'test123'

        phone = '+420602613357'
        body = 'Test'

        expected_json = {
            'login': app_config.sms_service_login,
            'password': app_config.sms_service_password,
            'phone': phone,
            'message': body,
            'sender': app_config.sms_service_sender
        }

        responses.add(
            'POST',
            url=app_config.sms_service_url,
            status=200,
            match=[
                json_params_matcher(expected_json)
            ]
        )

        _send_otp_ikem(recipient_phone=phone, message_body=body, app_config=app_config)

    @responses.activate
    def test__send_sms_should_fail(self):
        app_config = mock.MagicMock()
        app_config.sms_service_url = 'https://some.domain/SendSms'
        app_config.sms_service_sender = 'sender1'
        app_config.sms_service_login = 'test'
        app_config.sms_service_password = 'test123'

        phone = '+420602613357'
        body = 'Test'

        responses.add(
            'POST',
            url=app_config.sms_service_url,
            status=500,
            json='{\"error\":\"some error\"}'
        )

        self.assertRaises(
            CouldNotSendOtpUsingSmsServiceException,
            lambda: _send_otp_ikem(recipient_phone=phone, message_body=body, app_config=app_config)
        )
