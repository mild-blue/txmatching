import datetime
from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    VIEWER = 'VIEWER'
    EDITOR = 'EDITOR'
    SERVICE = 'SERVICE'


class TokenType(str, Enum):
    OTP = 'OTP'
    ACCESS = 'ACCESS'


@dataclass(frozen=True)
class EncodedBearerToken:
    user_id: int
    role: UserRole
    type: TokenType


@dataclass(frozen=True)
class BearerTokenRequest(EncodedBearerToken):
    expiration: datetime.timedelta
