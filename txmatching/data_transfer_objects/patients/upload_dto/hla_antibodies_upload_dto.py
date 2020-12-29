from dataclasses import dataclass

from txmatching.auth.exceptions import InvalidArgumentException


@dataclass
class HLAAntibodiesUploadDTO:
    name: str
    mfi: int
    cutoff: int

    def __post_init__(self):
        if self.mfi < 0:
            raise InvalidArgumentException("MFI should never be negative")
