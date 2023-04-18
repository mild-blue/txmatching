from dataclasses import dataclass
from typing import List, Optional, Set

from txmatching.utils.hla_system.detailed_score import DetailedScoreForHLAGroup

@dataclass
class RecipientDonorCompatibilityDetails:
    recipient_db_id: int
    donor_db_id: int
    score: float
    max_score: float
    compatible_blood: bool
    detailed_score: List[DetailedScoreForHLAGroup]


@dataclass
class RecipientDonorsCompatibility:
    cpra: Optional[int]
    compatible_donors: Set[int]
    compatible_donors_details: RecipientDonorCompatibilityDetails
