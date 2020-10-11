from typing import Iterator

from txmatching.solvers.matching.matching_with_score import MatchingWithScore


class SolverBase:
    def __init__(self):
        self.score_matrix = None

    def solve(self) -> Iterator[MatchingWithScore]:
        raise NotImplementedError('Has to be overridden')

    def get_score_matrix(self):
        return self.score_matrix
