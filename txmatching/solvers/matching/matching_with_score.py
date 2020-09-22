from typing import List

from txmatching.patients.donor_recipient_tuple import DonorRecipientTuple
from txmatching.solvers.matching.matching import Matching


class MatchingWithScore(Matching):
    """
    Set of disjoint TransplantRound's
    """

    def __init__(self, donor_recipient_list: List[DonorRecipientTuple], score: float, db_id: int):
        super().__init__(donor_recipient_list)
        self._score = score
        self._db_id = db_id

    def score(self) -> float:
        return self._score

    def db_id(self) -> int:
        return self._db_id

    def set_db_id(self, db_id: int):
        self._db_id = db_id
