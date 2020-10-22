from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.matchings.donor_recipient_dto import \
    DonorRecipientDTO


@dataclass
class CalculatedMatchingDTO:
    donors_recipients: List[DonorRecipientDTO]
    score: float
    db_id: int


@dataclass
class CalculatedMatchingsDTO:
    matchings: List[CalculatedMatchingDTO]
