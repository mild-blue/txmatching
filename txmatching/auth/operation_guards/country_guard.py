from typing import Union, Type

from txmatching.auth.exceptions import InvalidArgumentException, GuardException
from txmatching.database.services.app_user_management import get_app_user_by_id
from txmatching.database.sql_alchemy_schema import RecipientModel, DonorModel, AppUserModel
from txmatching.utils.enums import Country


def guard_user_country_access_to_donor(user_id: int, donor_id: int):
    """
    Verify that the user has correct country to access the donor.
    """
    _check_country(_get_user_checked(user_id), _get_resource_country_checked(donor_id, DonorModel))


def guard_user_country_access_to_recipient(user_id: int, recipient_id: int):
    """
    Verify that the user has correct country to access the recipient.
    """

    _check_country(_get_user_checked(user_id), _get_resource_country_checked(recipient_id, RecipientModel))


def guard_user_has_access_to(user_id: int, country: Country):
    """
    Verify that the user is allowed to access the country resources.
    """
    _check_country(_get_user_checked(user_id), country)


def _get_resource_country_checked(patient_id: int, model: Union[Type[RecipientModel], Type[DonorModel]]) -> Country:
    patient = model.query.get(patient_id)
    if not patient:
        raise InvalidArgumentException(f'{model.__name__} with id {patient} does not exist!')
    return patient.country


def _get_user_checked(user_id: int) -> AppUserModel:
    user = get_app_user_by_id(user_id)
    if not user:
        raise InvalidArgumentException(f'User with id {user_id} does not exist!')
    return user


def _check_country(user: AppUserModel, country: Country):
    if country not in user.get_allowed_edit_countries():
        raise GuardException(f'User id {user.id} does not have access to {country}!')
