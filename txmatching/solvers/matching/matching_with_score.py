from typing import List

from txmatching.patients.donor_recipient_tuple import DonorRecipientTuple
from txmatching.solvers.matching.matching import Matching


class MatchingWithScore(Matching):
    """
    Set of disjoint TransplantRound's
    """

    def __init__(self, donor_recipient_list: List[DonorRecipientTuple], score: float):
        super().__init__(donor_recipient_list)
        self._score = score

    def score(self) -> float:
        return self._score
