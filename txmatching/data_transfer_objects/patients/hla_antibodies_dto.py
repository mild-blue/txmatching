import logging
from dataclasses import dataclass, field
from typing import List

from txmatching.patients.hla_model import AntibodiesPerGroup, HLAAntibody

logger = logging.getLogger(__name__)


@dataclass
class HLAAntibodyUpdateDTO:
    raw_code: str
    mfi: int

    def __post_init__(self):
        if self.mfi < 0:
            self.mfi = 0
            logger.warning('MFI should not be negative, setting to 0.')


@dataclass
class HLAAntibodiesUpdateDTO:
    hla_antibodies_list: List[HLAAntibodyUpdateDTO] = field(default_factory=list)


@dataclass
class HLAAntibodiesDTO:
    # The field does not have default value because want dacite to raise exception if data stored in db are not valid
    hla_antibodies_list: List[HLAAntibody]
    hla_antibodies_per_groups: List[AntibodiesPerGroup]
