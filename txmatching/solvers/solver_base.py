from dataclasses import dataclass, field
from typing import Dict, Iterator, List

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.score_matrix import ScoreMatrix
from txmatching.solvers.all_solutions_solver.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.all_solutions_solver.scoring_utils import \
    get_score_for_idx_pairs
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


@dataclass(init=True)
class SolverBase:
    configuration: Configuration
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    scorer: AdditiveScorer
    donors: List[Donor] = field(init=False)
    recipients: List[Recipient] = field(init=False)
    score_matrix: ScoreMatrix = field(init=False)

    def __post_init__(self):
        self.donors = list(self.donors_dict.values())
        self.recipients = list(self.recipients_dict.values())
        self.score_matrix = self.scorer.get_score_matrix(
            self.recipients_dict,
            self.donors_dict
        )

    def solve(self) -> Iterator[MatchingWithScore]:
        raise NotImplementedError('Has to be overridden')

    def get_matching_from_path_combinations(
            self,
            found_pairs_idxs_only: List[DonorRecipientPairIdxOnly]) -> MatchingWithScore:
        found_pairs = list(DonorRecipientPair(self.donors[found_pair_idxs_only.donor_idx],
                                              self.recipients[found_pair_idxs_only.recipient_idx])
                           for found_pair_idxs_only in found_pairs_idxs_only)
        score = get_score_for_idx_pairs(self.score_matrix, found_pairs_idxs_only)
        return MatchingWithScore(found_pairs, score)
