import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HLAAntibodiesUploadDTO:
    name: str
    mfi: int
    cutoff: int

    def __post_init__(self):
        if self.mfi < 0:
            self.mfi = 0
            logger.warning("MFI should not be negative, setting to 0.")
