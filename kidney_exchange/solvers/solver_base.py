from typing import List, Iterator

from kidney_exchange.core.matching import Matching
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_base import ScorerBase


class SolverBase:
    def solve(self, donors: List[Donor], recipients: List[Recipient], scorer: ScorerBase) -> Iterator[Matching]:
        raise NotImplementedError("Has to be overriden")
