from typing import List, Iterator

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_base import ScorerBase
from kidney_exchange.solvers.matching.matching_with_score import MatchingWithScore


class SolverBase:
    def solve(self, donors: List[Donor],
              recipients: List[Recipient], scorer: ScorerBase) -> Iterator[MatchingWithScore]:
        raise NotImplementedError("Has to be overridden")

    @classmethod
    def from_config(cls, configuration: Configuration) -> "SolverBase":
        raise NotImplementedError("Has to be overridden")
