import logging
from dataclasses import dataclass
from typing import Dict, Iterator

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.solvers.all_solutions_solver.compatibility_graph_solver import \
    find_possible_path_combinations_from_compatibility_graph
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


# pylint: disable=abstract-method
@dataclass
class AllSolutionsSolver(SolverBase):
    config_parameters: ConfigParameters
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    scorer: AdditiveScorer

    def solve(self) -> Iterator[MatchingWithScore]:
        possible_path_combinations = find_possible_path_combinations_from_compatibility_graph(
            compatibility_graph=self.compatibility_graph,
            original_donor_idx_to_recipient_idx=self.original_donor_idx_to_recipient_idx,
            config_parameters=self.config_parameters,
            donors=list(self.donors)
        )

        for possible_path_combination in possible_path_combinations:
            yield self.get_matching_from_path_combinations(possible_path_combination)
