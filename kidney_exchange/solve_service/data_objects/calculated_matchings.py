from dataclasses import dataclass
from typing import List

from kidney_exchange.solve_service.data_objects.donor_recipient import DonorRecipient


@dataclass
class CalculatedMatching:
    donors_recipients: List[DonorRecipient]
    score: float


@dataclass
class CalculatedMatchings:
    matchings: List[CalculatedMatching]
