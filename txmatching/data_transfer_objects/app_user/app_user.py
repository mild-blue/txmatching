from dataclasses import dataclass

from txmatching.auth.data_types import UserRole


@dataclass
class AppUser:
    email: str
    role: UserRole
    default_txm_event_id: int
