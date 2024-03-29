import datetime
from unittest import TestCase

from txmatching.auth.data_types import BearerTokenRequest, TokenType, UserRole
from txmatching.auth.exceptions import (InvalidAuthCallException,
                                        InvalidIpAddressAccessException)
from txmatching.auth.service.service_auth import (
    SERVICE_JWT_EXPIRATION_MINUTES, service_login_flow)
from txmatching.database.sql_alchemy_schema import AppUserModel


class TestServiceAuth(TestCase):
    @staticmethod
    def _get_service(require_2fa: bool) -> AppUserModel:
        service = AppUserModel(
            email='email',
            pass_hash='hash',
            role=UserRole.SERVICE,
            second_factor_material='0.0.0.0',
            require_2fa=require_2fa
        )
        service.id = 10
        return service

    def test_service_login_flow(self):
        service = self._get_service(require_2fa=True)
        expected = BearerTokenRequest(
            user_id=service.id,
            role=UserRole.SERVICE,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(minutes=SERVICE_JWT_EXPIRATION_MINUTES)
        )

        token = service_login_flow(service, service.second_factor_material)
        self.assertEqual(expected, token)

    def test_service_login_flow_2fa_disabled(self):
        service = self._get_service(require_2fa=False)
        expected = BearerTokenRequest(
            user_id=service.id,
            role=UserRole.SERVICE,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(minutes=SERVICE_JWT_EXPIRATION_MINUTES)
        )

        token = service_login_flow(service, service.second_factor_material + '.0')
        self.assertEqual(expected, token)

    def test_service_login_flow_wrong_ip(self):
        service = self._get_service(require_2fa=True)
        self.assertRaises(InvalidIpAddressAccessException,
                          lambda: service_login_flow(service,
                                                     service.second_factor_material + '.1'))
        try:
            service_login_flow(service,
                               service.second_factor_material + '.1')
        except InvalidIpAddressAccessException as e:
            self.assertEqual(e.ip_address, '0.0.0.0.1')

    def test_service_login_flow_wrong_user(self):
        service = self._get_service(require_2fa=True)
        service.role = UserRole.ADMIN
        self.assertRaises(InvalidAuthCallException,
                          lambda: service_login_flow(service, service.second_factor_material))
