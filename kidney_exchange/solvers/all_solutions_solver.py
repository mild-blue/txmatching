from collections import Iterator
from typing import List

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_base import ScorerBase
from kidney_exchange.solvers.matching.matching import Matching
from kidney_exchange.solvers.solver_base import SolverBase


class AllSolutionsSolver(SolverBase):
    def solve(self, donors: List[Donor], recipients: List[Recipient], scorer: ScorerBase) -> Iterator[Matching]:
        raise NotImplementedError("TODO: Implement")  # TODO: Implement
