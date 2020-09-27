import datetime
from unittest import TestCase

from txmatching.auth.crypto.jwt_crypto import decode_auth_token, encode_auth_token, parse_request_token
from txmatching.auth.data_types import EncodedBearerToken, UserRole, TokenType
from txmatching.auth.exceptions import InvalidJWTException


class TestJwtCrypto(TestCase):
    # generated token, will start failing after 1917 years
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2Vy' \
            'X2lkIjoxLCJyb2xlIjoiQURNSU4iLCJ0eXBlIjoiQUNDR' \
            'VNTIiwiaWF0IjoxNjAxMDU3MjQ4LCJleHAiOjYyMDgxMD' \
            'U3MjQ4fQ.d9dVRLCi4uGmPc2GjrDY_G34Q5N7I2VD3EW1' \
            '0PLZWo0'
    secret = 'some-cool-secret-in-test'
    expected = EncodedBearerToken(1, UserRole.ADMIN, TokenType.ACCESS)

    def test_parse_request_token_failing(self):
        self.assertRaises(InvalidJWTException, lambda: parse_request_token('Bearer totally not a token', self.secret))
        self.assertRaises(InvalidJWTException, lambda: parse_request_token('Bearer NOT_TOKEN', self.secret))
        self.assertRaises(InvalidJWTException, lambda: parse_request_token(f'JWT {self.token}', self.secret))
        self.assertRaises(InvalidJWTException, lambda: parse_request_token('Bearer', self.secret))
        self.assertRaises(InvalidJWTException, lambda: parse_request_token('', self.secret))

    def test_parse_request_token(self):
        decoded = parse_request_token(f'Bearer {self.token}', self.secret)
        self.assertEqual(self.expected, decoded)

    def test_decode_auth_token(self):
        bearer = decode_auth_token(self.token, self.secret)
        self.assertEqual(self.expected, bearer)

    def test_encode_decode(self):
        encoded = encode_auth_token(self.expected.user_id, self.expected.role, self.expected.type,
                                    datetime.timedelta(minutes=1), self.secret)
        decoded = decode_auth_token(encoded, self.secret)
        self.assertEqual(self.expected, decoded)
