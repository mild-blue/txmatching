from typing import List
from unittest import mock
from uuid import uuid4

from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import GuardException
from txmatching.auth.operation_guards.country_guard import (
    guard_user_country_access_to_donor, guard_user_country_access_to_recipient,
    guard_user_has_access_to_country)
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.database.services.app_user_management import persist_user
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.utils.country_enum import Country


class TestCountryGuards(DbTests):

    def _create_user(self, allowed_countries: List[Country]) -> int:
        user = AppUserModel(
            email=str(uuid4),
            pass_hash=encode_password('password'),
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            require_2fa=False,
            allowed_edit_countries=allowed_countries
        )
        self.assertEqual(len(allowed_countries), len(user.allowed_edit_countries))
        for allowed in allowed_countries:
            self.assertTrue(allowed in user.allowed_edit_countries)

        return persist_user(user).id

    def _create_model_mock(self, patient_id: int, country: Country) -> mock:
        model = mock.MagicMock()
        query = mock.MagicMock()
        model.query = query

        patient = mock.MagicMock()
        patient.country = country

        def get_mock(db_id):
            self.assertEqual(db_id, patient_id)
            return patient

        query.get = get_mock
        return model

    def test_guard_user_has_access_to(self):
        patient_country = Country.CZE
        user_id = self._create_user([patient_country, Country.ISR])
        guard_user_has_access_to_country(user_id, patient_country)

    def test_guard_user_has_access_to_should_fail(self):
        patient_country = Country.CZE
        # noinspection PyTypeChecker
        # Pycharm enum/str problems
        user_id = self._create_user([country for country in Country if country != patient_country])
        self.assertRaises(GuardException, lambda: guard_user_has_access_to_country(user_id, Country.CZE))

    def test_guard_user_country_access_to_donor(self):
        patient_country = Country.CZE
        patient_id = 10

        user_id = self._create_user([patient_country, Country.ISR])
        model_mock = self._create_model_mock(patient_id, patient_country)

        with mock.patch('txmatching.auth.operation_guards.country_guard.DonorModel', model_mock):
            guard_user_country_access_to_donor(user_id, patient_id)

    def test_guard_user_country_access_to_donor_should_fail(self):
        patient_country = Country.CZE
        patient_id = 1

        user_id = self._create_user([Country.IND, Country.ISR])
        model_mock = self._create_model_mock(patient_id, patient_country)

        with mock.patch('txmatching.auth.operation_guards.country_guard.DonorModel', model_mock):
            self.assertRaises(GuardException, lambda: guard_user_country_access_to_donor(user_id, patient_id))

    def test_guard_user_country_access_to_recipient(self):
        patient_country = Country.ISR
        patient_id = 12

        user_id = self._create_user([patient_country, Country.ISR])
        model_mock = self._create_model_mock(patient_id, patient_country)

        with mock.patch('txmatching.auth.operation_guards.country_guard.RecipientModel', model_mock):
            guard_user_country_access_to_recipient(user_id, patient_id)

    def test_guard_user_country_access_to_recipient_should_fail(self):
        patient_country = Country.CZE
        patient_id = 15

        user_id = self._create_user([Country.ISR])
        model_mock = self._create_model_mock(patient_id, patient_country)

        with mock.patch('txmatching.auth.operation_guards.country_guard.RecipientModel', model_mock):
            self.assertRaises(GuardException, lambda: guard_user_country_access_to_recipient(user_id, patient_id))
