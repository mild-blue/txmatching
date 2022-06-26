import logging
from dataclasses import dataclass

from txmatching.auth.exceptions import InvalidArgumentException

logger = logging.getLogger(__name__)


@dataclass
class HLAAntibodiesUploadDTO:
    name: str
    mfi: int
    cutoff: int

    def __post_init__(self):
        if self.mfi < 0:
            raise InvalidArgumentException('Some antibodies have negative MFI value.')
        if self.cutoff < 0:
            raise InvalidArgumentException('Some antibodies have negative cutoff value.')
