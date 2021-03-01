import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Tuple

from txmatching.solvers.all_solutions_solver.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.ilp_solver.prepare_data_for_ilp_solver import \
    prepare_data_for_ilp
from txmatching.solvers.ilp_solver.solve_ilp import solve_ilp
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


@dataclass
class ILPSolver(SolverBase):

    def solve(self) -> Iterator[MatchingWithScore]:
        config_for_ilp_solver = prepare_data_for_ilp(self.donors_dict, self.recipients_dict, self.configuration)
        solutions = solve_ilp(config_for_ilp_solver)
        recipients_db_id_to_order_id = {
            recipient.db_id: order_id for order_id, recipient in enumerate(self.recipients)
        }

        for solution in solutions:
            possible_path_combination = self._get_path_combinations(solution.edges, recipients_db_id_to_order_id)

            yield self.get_matching_from_path_combinations(possible_path_combination)

    def _get_path_combinations(self,
                               donor_idx_tuples: Iterable[Tuple[int, int]],
                               recipients_db_id_to_order_id: Dict[int, int]) -> List[DonorRecipientPairIdxOnly]:
        return [
            DonorRecipientPairIdxOnly(
                donor_idx=donor_idx,
                recipient_idx=recipients_db_id_to_order_id[
                    self.donors[idx_of_donor_for_recipient].related_recipient_db_id]
            )
            for donor_idx, idx_of_donor_for_recipient in donor_idx_tuples
        ]
