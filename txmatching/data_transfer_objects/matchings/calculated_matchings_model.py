from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.matchings.donor_recipient_dto import \
    DonorRecipientDTO


@dataclass
class CalculatedMatchingModel:
    donors_recipients: List[DonorRecipientDTO]
    score: float
    db_id: int


@dataclass
class CalculatedMatchingsModel:
    calculated_matchings: List[CalculatedMatchingModel]
    found_matchings_count: int
    all_matchings_found: bool
