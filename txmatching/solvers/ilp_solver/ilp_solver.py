# pylint: skip-file
# TODO: improve the code https://github.com/mild-blue/txmatching/issues/430

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Tuple

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.solvers.all_solutions_solver.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.all_solutions_solver.scoring_utils import \
    get_score_for_idx_pairs
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.ilp_solver.anderson_recursive_nocb import (
    MaxSequenceLimitMethod, ObjectiveType, SolverConfig, solve_ilp)
from txmatching.solvers.ilp_solver.prepare_data_for_ilp_solver import \
    prepare_data_for_ilp
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


@dataclass
class ILPSolver(SolverBase):
    configuration: Configuration
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    scorer: AdditiveScorer

    def __post_init__(self):
        self.donors = list(self.donors_dict.values())
        self.recipients = list(self.recipients_dict.values())

        self.recipients_db_id_to_order_id = {
            recipient.db_id: order_id for order_id, recipient in enumerate(self.recipients)
        }

        self.score_matrix = self.scorer.get_score_matrix(
            self.donors,
            self.recipients,
            self.donors_dict
        )

        self.config_for_ilp_solver = prepare_data_for_ilp(self.donors_dict, self.recipients_dict, self.configuration)

    def solve(self) -> Iterator[MatchingWithScore]:
        solver_config = SolverConfig(
            objective_type=ObjectiveType.MaxTransplantsMaxWeights,
            max_sequence_limit_method=MaxSequenceLimitMethod.LazyForbidAllMaximalSequences
        )
        ilp_solution = solve_ilp(self.config_for_ilp_solver, solver_config).solution
        if ilp_solution is not None:
            possible_path_combination = self.get_path_combinations(ilp_solution.edges)

            yield self._get_matching_from_path_combinations(possible_path_combination)
        return

    def _get_matching_from_path_combinations(
            self, found_pairs_idxs_only: List[DonorRecipientPairIdxOnly]
    ) -> MatchingWithScore:
        found_pairs = frozenset(DonorRecipientPair(self.donors[found_pair_idxs_only.donor_idx],
                                                   self.recipients[found_pair_idxs_only.recipient_idx])
                                for found_pair_idxs_only in found_pairs_idxs_only)
        score = get_score_for_idx_pairs(self.score_matrix, found_pairs_idxs_only)
        return MatchingWithScore(found_pairs, score)

    def get_path_combinations(self, donor_idx_tuples: Iterable[Tuple[int, int]]) -> List[DonorRecipientPairIdxOnly]:
        return [
            DonorRecipientPairIdxOnly(
                donor_idx=donor_idx,
                recipient_idx=self.recipients_db_id_to_order_id[
                    self.donors[idx_of_donor_for_recipient].related_recipient_db_id]
            )
            for donor_idx, idx_of_donor_for_recipient in donor_idx_tuples
        ]
