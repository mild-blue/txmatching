from dataclasses import dataclass, field
from typing import List, Tuple

from kidney_exchange.config.configuration import Configuration

MAN_DON_REC_SCORES_DTO = 'manual_donor_recipient_scores_dto'


@dataclass
class DonorRecipientScoreDTO:
    donor_medical_id: str
    recipient_medical_id: str
    score: float


@dataclass
class ConfigurationDTO(Configuration):
    manual_donor_recipient_scores_dto: List[Tuple[str, str, float]] = field(default_factory=list)
