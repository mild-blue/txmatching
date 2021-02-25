from dataclasses import dataclass
from typing import Optional

from txmatching.solvers.matching.matching import Matching


@dataclass()
class MatchingWithScore(Matching):
    """
    Set of disjoint TransplantRound's
    """
    score: float
    order_id: Optional[int] = None

    def set_order_id(self, order_id: int):
        self.order_id = order_id

    def __hash__(self):
        return self.get_donor_recipient_pairs().__hash__()
