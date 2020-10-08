from unittest import TestCase, mock

import responses

from txmatching.auth.user.sms_service import _send_otp_ikem


class TestSmsService(TestCase):
    @responses.activate
    def test__send_sms(self):
        app_config = mock.MagicMock()
        app_config.sms_service_url = 'https://some.domain/isg/index.php'
        app_config.sms_service_sender = 'sender1'
        app_config.sms_service_login = 'test'
        app_config.sms_service_password = 'test123'

        phone = '+420602613357'
        body = 'Test'

        # encoded URL for the previous input
        expected_url = 'https://some.domain/isg/index.php?' \
                       'cmd=send&' \
                       'sender=sender1&' \
                       'login=test&' \
                       'password=test123&' \
                       'phone=%2B420602613357&' \
                       'message=Test'

        responses.add(
            'GET',
            url=expected_url,
            match_querystring=True
        )

        _send_otp_ikem(recipient_phone=phone, message_body=body, app_config=app_config)
