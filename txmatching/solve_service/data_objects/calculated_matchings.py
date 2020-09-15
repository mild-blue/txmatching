from dataclasses import dataclass
from typing import List

from txmatching.solve_service.data_objects.donor_recipient import DonorRecipient


@dataclass
class CalculatedMatching:
    donors_recipients: List[DonorRecipient]
    score: float
    db_id: int


@dataclass
class CalculatedMatchings:
    matchings: List[CalculatedMatching]
