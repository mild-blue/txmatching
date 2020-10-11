from dataclasses import dataclass
from typing import List

from txmatching.solve_service.data_objects.donor_recipient import \
    DonorIdRecipientIdPair


@dataclass
class CalculatedMatching:
    donors_recipients: List[DonorIdRecipientIdPair]
    score: float
    db_id: int


@dataclass
class CalculatedMatchings:
    matchings: List[CalculatedMatching]
