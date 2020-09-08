from typing import Iterator, List

from txmatching.config.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.scorers.scorer_base import ScorerBase
from txmatching.solvers.matching.matching_with_score import \
    MatchingWithScore


class SolverBase:
    def solve(self, donors: List[Donor],
              recipients: List[Recipient], scorer: ScorerBase) -> Iterator[MatchingWithScore]:
        raise NotImplementedError('Has to be overridden')

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'SolverBase':
        raise NotImplementedError('Has to be overridden')
