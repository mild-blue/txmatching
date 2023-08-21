from unittest import TestCase

from txmatching.auth.crypto.password_crypto import (encode_password,
                                                    password_matches_hash)


class TestPasswordCrypto(TestCase):
    def test_encode_decode_password(self):
        self.assertTrue(password_matches_hash(encode_password('hello'), 'hello'))
        self.assertFalse(password_matches_hash(encode_password('hello'), 'false'))
