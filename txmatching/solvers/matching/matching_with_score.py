from typing import List

from txmatching.patients.donor_recipient_tuple import DonorRecipientTuple
from txmatching.solvers.matching.matching import Matching


class MatchingWithScore(Matching):
    """
    Set of disjoint TransplantRound's
    """

    def __init__(self, donor_recipient_list: List[DonorRecipientTuple], score: float, idd: str):
        super().__init__(donor_recipient_list)
        self._score = score
        self._id = idd

    def score(self) -> float:
        return self._score

    def id(self) -> str:
        return self._id
