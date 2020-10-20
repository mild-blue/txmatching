import logging
from typing import Iterable, Tuple

import numpy as np

from txmatching.filters.filter_from_config import filter_from_config
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solve_service.data_objects.solver_input_parameters import \
    SolverInputParameters
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_from_config import solver_from_config

logger = logging.getLogger(__name__)


def solve_from_config(params: SolverInputParameters) -> Tuple[Iterable[MatchingWithScore], np.array]:
    scorer = scorer_from_configuration(params.configuration)
    solver = solver_from_config(params.configuration)
    score_matrix = scorer.get_score_matrix(
        params.txm_event.donors_dict, params.txm_event.recipients_dict
    )

    all_solutions = solver.solve(params.txm_event.donors_dict, params.txm_event.recipients_dict, scorer)

    matching_filter = filter_from_config(params.configuration)
    matchings_filtered = filter(matching_filter.keep, all_solutions)

    matchings = list(matchings_filtered)
    matchings.sort(key=lambda matching: len(matching.get_rounds()), reverse=True)
    matchings.sort(key=lambda matching: matching.score(), reverse=True)
    matchings.sort(key=lambda matching: len(matching.donor_recipient_list), reverse=True)
    for idx, matching in enumerate(matchings):
        matching.set_order_id(idx + 1)

    return matchings, score_matrix
