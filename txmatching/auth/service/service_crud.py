import socket

from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import UserUpdateException
from txmatching.database.services.app_user_management import persist_user, get_app_user_by_email, \
    update_password_for_user
from txmatching.database.sql_alchemy_schema import AppUserModel


def register_service(email: str, password: str, whitelisted_ip: str) -> AppUserModel:
    """
    Registers new service for given email, password and whitelisted_ip.
    """
    _assert_service_registration(email, password, whitelisted_ip)
    user = AppUserModel(
        email=email,
        pass_hash=encode_password(password),
        role=UserRole.SERVICE,
        second_factor_material=whitelisted_ip
    )
    persist_user(user)
    return user


def change_service_password(user_id: int, new_password: str):
    """
    Updates password for the service.
    """
    _assert_service_password_validity(new_password)
    pwd_hash = encode_password(new_password)
    update_password_for_user(user_id=user_id, new_password_hash=pwd_hash)


def _assert_service_registration(email: str, password: str, whitelisted_ip: str):
    if not email:
        raise UserUpdateException('Invalid email address.')
    if not whitelisted_ip:
        raise UserUpdateException('Missing IP Address')
    if get_app_user_by_email(email):
        raise UserUpdateException('The e-mail address is already in use.')

    _assert_service_password_validity(password)
    _assert_ip_address(whitelisted_ip)


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
