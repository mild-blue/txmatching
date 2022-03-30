from dataclasses import dataclass, field
from typing import List, Optional

from txmatching.auth.data_types import UserRole
from txmatching.utils.country_enum import Country


@dataclass
class UserRegistrationDtoIn:
    email: str
    password: str
    role: UserRole
    second_factor: str
    allowed_countries: List[Country]
    allowed_txm_events: List[str]
    require_second_factor: bool


@dataclass
class UserRegistrationDtoOut:
    email: str
    role: UserRole
    allowed_countries: List[Country]
    allowed_txm_events: List[str]
    password_reset_token: str
    password_reset_token_message: str
