import time
from typing import Optional

from txmatching.database.sql_alchemy_schema import AppUserModel


# noinspection PyUnusedLocal
# pylint: disable=unused-argument
# will be used in the proper implementation
def auth_failed_slow_down(user: Optional[AppUserModel]):
    """
    Slows down request response if the authentication failed.
    Should be used as a defense against attacker trying to bruteforce the passwords.
    """
    # sleep for 2 seconds before sending back the reply
    # is a poor man's solution for slowing down the possible attacker
    # that is using bruteforce attack
    # will be properly solved here TODO https://trello.com/c/eqUJ2ux8
    time.sleep(2)
