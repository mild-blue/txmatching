from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.matchings.donor_recipient_model import \
    DonorRecipientModel


@dataclass
class MatchingModel:
    donors_recipients: List[DonorRecipientModel]
    score: float
    db_id: int


@dataclass
class MatchingsModel:
    matchings: List[MatchingModel]
    found_matchings_count: Optional[int]
    show_not_all_matchings_found: bool
