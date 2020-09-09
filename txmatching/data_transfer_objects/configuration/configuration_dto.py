from dataclasses import dataclass, field
from typing import List, Tuple

from txmatching.config.configuration import ConfigurationBase

MAN_DON_REC_SCORES_DTO = 'manual_donor_recipient_scores_dto'


@dataclass
class ConfigurationDTO(ConfigurationBase):
    manual_donor_recipient_scores_dto: List[Tuple[str, str, float]] = field(default_factory=list)
