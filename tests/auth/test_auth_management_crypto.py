import time
from datetime import timedelta
from unittest import TestCase
from uuid import uuid4

from txmatching.auth.auth_management import _get_reset_token, _verify_reset_token
from txmatching.auth.exceptions import InvalidTokenException


class TestAuthManagementCrypto(TestCase):

    def test_token_flow(self):
        key = str(uuid4())
        user_id = 10
        token = _get_reset_token(key, user_id)

        parsed_user_id = _verify_reset_token(key, token)
        self.assertEqual(user_id, parsed_user_id)

    def test_wrong_token(self):
        key = str(uuid4())
        user_id = 10
        token = _get_reset_token(key, user_id)

        # test signature is invalid
        self.assertRaises(InvalidTokenException,
                          lambda: _verify_reset_token(key, token + 'p'))
        # test signature doesn't match
        self.assertRaises(InvalidTokenException,
                          lambda: _verify_reset_token(key, 'p' + token))

    def test_token_expired(self):
        key = str(uuid4())
        user_id = 10
        token = _get_reset_token(key, user_id)
        expiration = timedelta(seconds=1)
        # test that the token is valid
        self.assertEqual(user_id, _verify_reset_token(key, token, expiration))
        # let the token expire
        # granularity of the signing library is 1s, thus we need to sleep a bit more
        time.sleep(2)
        # test that the signature is valid
        self.assertRaises(InvalidTokenException,
                          lambda: _verify_reset_token(key, token, expiration))
