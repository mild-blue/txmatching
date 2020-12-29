import logging
from dataclasses import dataclass
from typing import Dict, Iterator, List

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.solvers.all_solutions_solver.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.all_solutions_solver.score_matrix_solver import \
    find_possible_path_combinations_from_score_matrix
from txmatching.solvers.all_solutions_solver.scoring_utils import \
    get_score_for_idx_pairs
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


@dataclass
class AllSolutionsSolver(SolverBase):
    configuration: Configuration
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    scorer: AdditiveScorer

    def __post_init__(self):
        self.donors = sorted(list(self.donors_dict.values()), key=lambda x: x.medical_id[:-4])
        self.recipients = sorted(list(self.recipients_dict.values()), key=lambda x: x.medical_id[-3:])

        self.score_matrix = self.scorer.get_score_matrix(
            self.donors,
            self.recipients,
            self.donors_dict
        )

    def solve(self) -> Iterator[MatchingWithScore]:
        possible_path_combinations = find_possible_path_combinations_from_score_matrix(
            score_matrix=self.score_matrix,
            configuration=self.configuration,
            donors=self.donors
        )

        for possible_path_combination in possible_path_combinations:
            yield self._get_matching_from_path_combinations(possible_path_combination)

    def _get_matching_from_path_combinations(
            self, found_pairs_idxs_only: List[DonorRecipientPairIdxOnly]
    ) -> MatchingWithScore:
        found_pairs = frozenset(DonorRecipientPair(self.donors[found_pair_idxs_only.donor_idx],
                                                   self.recipients[found_pair_idxs_only.recipient_idx])
                                for found_pair_idxs_only in found_pairs_idxs_only)
        score = get_score_for_idx_pairs(self.score_matrix, found_pairs_idxs_only)
        return MatchingWithScore(found_pairs, score)
