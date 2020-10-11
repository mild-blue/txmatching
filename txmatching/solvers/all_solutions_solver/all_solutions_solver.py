# pylint: skip-file
# at the moment the solver is not optimal but works alright. We do not want to invest time in its improvement
# at the moment as later there might be some complete rewrite of it if it bothers us.
import logging
from dataclasses import dataclass
from typing import Dict, Iterator, List

import numpy as np

from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.solve_service.data_objects.donor_recipient import \
    DonorIdRecipientIdPair
from txmatching.solvers.all_solutions_solver.find_possible_solution_pairs import \
    find_possible_solution_pairs_from_score_matrix
from txmatching.solvers.all_solutions_solver.helper_functions import \
    get_score_for_pairs
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


@dataclass
class AllSolutionsSolver(SolverBase):
    max_number_of_distinct_countries_in_round: int
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    scorer: AdditiveScorer

    def __post_init__(self):
        self.score_matrix = self.scorer.get_score_matrix(
            self.donors_dict,
            self.recipients_dict
        )
        self.recipients = list(self.recipients_dict.values())
        self.donors = list(self.donors_dict.values())
        self.score_matrix_array = np.zeros((len(self.donors), len(self.recipients)))
        for row_index, row in enumerate(self.score_matrix):
            for column_index, value in enumerate(row):
                self.score_matrix_array[row_index, column_index] = value

    def solve(self) -> Iterator[MatchingWithScore]:

        returned_matchings = set()
        pairs_for_solutions = find_possible_solution_pairs_from_score_matrix(score_matrix=self.score_matrix_array)

        for solution_pairs in pairs_for_solutions:
            matching = self._get_matching_from_pairs(solution_pairs)

            valid_number_of_countries = max([transplant_round.country_count for transplant_round in
                                             matching.get_rounds()]) <= self.max_number_of_distinct_countries_in_round
            if valid_number_of_countries:
                if matching not in returned_matchings:
                    yield matching
                    returned_matchings.add(matching)
            else:
                cleaned_matching = self._clean_matching_of_too_many_countries(matching)
                if cleaned_matching not in returned_matchings:
                    yield cleaned_matching
                    returned_matchings.add(cleaned_matching)

    def _get_matching_from_pairs(self, solution_pairs: List[DonorIdRecipientIdPair]):
        solution_pairs_enriched = frozenset(DonorRecipientPair(self.donors[solution_pair.donor],
                                                               self.recipients[solution_pair.recipient])
                                            for solution_pair in solution_pairs
                                            )
        score = get_score_for_pairs(self.score_matrix_array, solution_pairs)
        return MatchingWithScore(solution_pairs_enriched, score)

    def _clean_matching_of_too_many_countries(self, matching: MatchingWithScore):
        proper_rounds = [transplant_round for transplant_round in
                         matching.get_rounds() if
                         transplant_round.country_count <= self.max_number_of_distinct_countries_in_round]

        if len(proper_rounds) > 0:
            solution_pairs_enriched = frozenset(
                donor_recipient for transplant_round in proper_rounds for donor_recipient
                in
                transplant_round.donor_recipient_list)

            score = get_score_for_pairs(self.score_matrix_array, solution_pairs_enriched)
            return MatchingWithScore(solution_pairs_enriched, score)
