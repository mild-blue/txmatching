from typing import FrozenSet

from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching import Matching


class MatchingWithScore(Matching):
    """
    Set of disjoint TransplantRound's
    """

    def __init__(self, donor_recipient_list: FrozenSet[DonorRecipientPair], score: float, order_id: int = 0):
        super().__init__(donor_recipient_list)
        self._score = score
        self._order_id = order_id

    def score(self) -> float:
        return self._score

    def order_id(self) -> int:
        return self._order_id

    def set_order_id(self, order_id: int):
        self._order_id = order_id

    def __hash__(self):
        return self.donor_recipient_pairs.__hash__()
