import logging
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterator, List, Optional

import numpy as np

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
        self.score_matrix = self.scorer.get_score_matrix(
            self.donors_dict,
            self.recipients_dict
        )
        self.score_matrix_array = np.zeros((len(self.donors_dict), len(self.recipients_dict)))
        for row_index, row in enumerate(self.score_matrix):
            for column_index, value in enumerate(row):
                self.score_matrix_array[row_index, column_index] = value

    def solve(self) -> Iterator[MatchingWithScore]:

        matchings_to_return = set()
        possible_path_combinations = find_possible_path_combinations_from_score_matrix(
            score_matrix=self.score_matrix_array,
            configuration=self.configuration
        )

        for possible_path_combination in possible_path_combinations:
            matching = self._get_matching_from_path_combinations(possible_path_combination)

            valid_number_of_countries = max(
                [transplant_round.country_count for transplant_round in
                 matching.get_rounds()]) <= self.configuration.max_number_of_distinct_countries_in_round
            if valid_number_of_countries:
                if matching not in matchings_to_return:
                    yield matching
                    matchings_to_return.add(matching)
            else:
                cleaned_matching = self._remove_rounds_with_too_many_countries(matching)
                if cleaned_matching not in matchings_to_return:
                    yield cleaned_matching
                    matchings_to_return.add(cleaned_matching)

    def _get_matching_from_path_combinations(
            self, found_pairs_idxs_only: List[DonorRecipientPairIdxOnly]
    ) -> MatchingWithScore:

        donors = list(self.donors_dict.values())
        recipients = list(self.recipients_dict.values())
        found_pairs = frozenset(DonorRecipientPair(donors[found_pair_indeces_only.donor_idx],
                                                   recipients[found_pair_indeces_only.recipient_idx])
                                for found_pair_indeces_only in found_pairs_idxs_only)
        score = get_score_for_idx_pairs(self.score_matrix_array, found_pairs_idxs_only)
        return MatchingWithScore(found_pairs, score)

    # TODO This whole function will be removed in https://trello.com/c/AREDzFnQ, now quick fix to make it work
    def _remove_rounds_with_too_many_countries(self, matching: MatchingWithScore) -> Optional[MatchingWithScore]:
        proper_rounds = [transplant_round for transplant_round in
                         matching.get_rounds() if
                         transplant_round.country_count <= self.configuration.max_number_of_distinct_countries_in_round]

        if len(proper_rounds) > 0:
            solution_pairs_enriched = frozenset(
                donor_recipient for transplant_round in proper_rounds for donor_recipient
                in
                transplant_round.donor_recipient_list)

            score = self._get_score_for_enriched_pairs(solution_pairs_enriched)
            return MatchingWithScore(solution_pairs_enriched, score)
        else:
            return None

    # TODO This whole function will be removed in https://trello.com/c/AREDzFnQ, no quick fix to make it work
    def _get_score_for_enriched_pairs(self, solution_pairs_enriched: FrozenSet[DonorRecipientPair]) -> int:
        return sum([
            self.scorer.score_transplant(pair.donor,
                                         pair.recipient,
                                         self.donors_dict[pair.recipient.related_donor_db_id])
            for pair in solution_pairs_enriched
        ])
