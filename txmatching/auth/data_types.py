from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    VIEWER = 'VIEWER'
    EDITOR = 'EDITOR'
    SERVICE = 'SERVICE'


@dataclass
class LoginSuccessResponse:
    auth_token: str


@dataclass
class FailResponse:
    error: str


@dataclass(frozen=True)
class BearerToken:
    user_id: int
    role: UserRole
