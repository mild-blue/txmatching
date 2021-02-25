import logging
from dataclasses import dataclass
from typing import Dict, Iterator

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.solvers.all_solutions_solver.score_matrix_solver import \
    find_possible_path_combinations_from_score_matrix
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


@dataclass
class AllSolutionsSolver(SolverBase):
    configuration: Configuration
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    scorer: AdditiveScorer

    def solve(self) -> Iterator[MatchingWithScore]:
        possible_path_combinations = find_possible_path_combinations_from_score_matrix(
            score_matrix=self.score_matrix,
            configuration=self.configuration,
            donors=list(self.donors)
        )

        for possible_path_combination in possible_path_combinations:
            yield self.get_matching_from_path_combinations(possible_path_combination)
