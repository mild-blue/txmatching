from dataclasses import dataclass
from typing import List, Optional

from txmatching.patients.patient import Donor
from txmatching.utils.hla_system.detailed_score import DetailedScoreForHLAGroup


@dataclass
class DonorDTOOut(Donor):
    score_with_related_recipient: Optional[float] = None
    detailed_score_with_related_recipient: Optional[List[DetailedScoreForHLAGroup]] = None
    compatible_blood_with_related_recipient: Optional[str] = None
