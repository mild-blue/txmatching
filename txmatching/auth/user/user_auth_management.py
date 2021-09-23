import re
from typing import List, Optional

from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import (UserUpdateException,
                                        require_auth_condition)
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.database.services.app_user_management import (
    get_app_user_by_email, persist_user, update_password_for_user)
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.utils.country_enum import Country


# pylint: disable=too-many-arguments
# not worth the effor as it is just an admin API
def register_user(email: str, password: str, allowed_countries: List[Country], require_second_factor: bool,
                  phone_number: str, role: UserRole) -> AppUserModel:
    """
    Registers new user for given email, password and role.
    """
    require_auth_condition(role != UserRole.SERVICE, f'{role} used for registering user!')

    normalized_email = email.lower()
    _assert_user_registration(normalized_email, password, require_second_factor, phone_number, role)

    user = AppUserModel(
        email=normalized_email,
        pass_hash=encode_password(password),
        role=role,
        second_factor_material=generate_totp_seed(),
        phone_number=phone_number,
        allowed_edit_countries=allowed_countries,
        require_2fa=require_second_factor
    )
    persist_user(user)
    return user


def change_user_password(user_id: int, new_password: str):
    """
    Updates password for the user.
    """
    _assert_user_password_validity(new_password)
    password_hash = encode_password(new_password)
    update_password_for_user(user_id=user_id, new_password_hash=password_hash)


def _assert_user_registration(normalized_email: str, password: str, require_second_factor: bool,
                              phone_number: Optional[str], role: Optional[UserRole]):
    if not normalized_email:
        raise UserUpdateException('Invalid email address.')
    if not role:
        raise UserUpdateException('Invalid user role.')
    if get_app_user_by_email(normalized_email):
        raise UserUpdateException('The e-mail address is already in use.')
    _assert_user_password_validity(password)
    if require_second_factor:
        _assert_phone_number_validity(phone_number)
    else:
        if phone_number:
            raise UserUpdateException('Phone number should not be filled in in case second factor is disabled.')


def _assert_phone_number_validity(phone_number: str):
    if not phone_number:
        raise UserUpdateException('Empty phone number submitted!')
    # no advanced validation, just check if the phone number
    # starts with + and contains just the numbers
    if not re.match(r'^\+\d+$', phone_number):
        raise UserUpdateException(f'Invalid phone number! The following phone number '
                                  f'is valid +420654789123. Received {phone_number}.')


def _assert_user_password_validity(password: str):
    # TODO https://trello.com/c/ivSt018y define our password policies for the users
    if not password:
        raise UserUpdateException('Invalid password.')
