import socket
from typing import List

from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import UserUpdateException
from txmatching.database.services.app_user_management import (
    get_app_user_by_email, persist_user, update_password_for_user)
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.utils.country_enum import Country


def register_service(email: str, password: str, allowed_countries: List[Country], require_second_factor: bool,
                     whitelisted_ip: str) -> AppUserModel:
    """
    Registers new service for given email, password and whitelisted_ip.
    """
    normalized_email = email.lower()
    _assert_service_registration(normalized_email, password,
                                 require_second_factor, whitelisted_ip)
    user = AppUserModel(
        email=normalized_email,
        pass_hash=encode_password(password),
        role=UserRole.SERVICE,
        second_factor_material=whitelisted_ip,
        allowed_edit_countries=allowed_countries,
        require_2fa=require_second_factor
    )
    persist_user(user)
    return user


def change_service_password(user_id: int, new_password: str):
    """
    Updates password for the service account.
    """
    _assert_service_password_validity(new_password)
    pwd_hash = encode_password(new_password)
    update_password_for_user(user_id=user_id, new_password_hash=pwd_hash)


def _assert_service_registration(normalized_email: str, password: str, require_second_factor: bool,
                                 whitelisted_ip: str):
    if not normalized_email:
        raise UserUpdateException('Invalid email address.')

    if get_app_user_by_email(normalized_email):
        raise UserUpdateException('The e-mail address is already in use.')
    _assert_service_password_validity(password)
    if require_second_factor:
        if not whitelisted_ip:
            raise UserUpdateException('Missing IP Address.')
        _assert_ip_address(whitelisted_ip)
    else:
        if whitelisted_ip:
            raise UserUpdateException('IP address should not be filled in the case second factor is disabled.')


def _assert_service_password_validity(password: str):
    # TODO https://trello.com/c/ivSt018y define our password policies for the services
    if not password:
        raise UserUpdateException('Invalid password.')


def _assert_ip_address(address: str):
    if not _is_valid_ipv4_address(address) and not _is_valid_ipv6_address(address):
        raise UserUpdateException('Invalid IP address!')


# https://stackoverflow.com/a/4017219/7169288
def _is_valid_ipv4_address(address: str) -> bool:
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False
    return True


def _is_valid_ipv6_address(address: str) -> bool:
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:
        return False
    return True
