from typing import List, Tuple

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.matching import Matching


class MatchingWithScore(Matching):
    """
    Set of disjoint TransplantRound's
    """

    def __init__(self, donor_recipient_list: List[Tuple[Donor, Recipient]], score: float):
        super().__init__(donor_recipient_list)
        self._score = score

    def score(self) -> float:
        return self._score
