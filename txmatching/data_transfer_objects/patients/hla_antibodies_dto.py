import logging
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger(__name__)


# TODOO: prob rename, used in update
@dataclass
class HLAAntibodyDTO:
    raw_code: str
    mfi: int

    def __post_init__(self):
        if self.mfi < 0:
            self.mfi = 0
            logger.warning('MFI should not be negative, setting to 0.')


@dataclass
class HLAAntibodiesDTO:
    hla_antibodies_list: List[HLAAntibodyDTO] = field(default_factory=list)


@dataclass
class HLAAntibodyParsedDTO:
    raw_code: str
    code: str
    mfi: int
    cutoff: int


# TODOO: prob rename when renamed above
@dataclass
class HLAAntibodiesParsedDTO:
    hla_antibodies_list: List[HLAAntibodyParsedDTO] = field(default_factory=list)
