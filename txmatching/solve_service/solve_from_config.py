import logging
from typing import Iterable, Tuple

import numpy as np

from txmatching.config.configuration import Configuration
from txmatching.database.services.matching_service import load_matchings_from_database
from txmatching.filters.filter_from_config import filter_from_config
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solve_service.data_objects.solver_input_parameters import SolverInputParameters
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_from_config import solver_from_config

logger = logging.getLogger(__name__)


def solve_from_config(params: SolverInputParameters) -> Tuple[Iterable[MatchingWithScore], np.array]:
    scorer = scorer_from_configuration(params.configuration)
    solver = solver_from_config(params.configuration)
    matchings_in_db = load_matchings_from_database(params)
    score_matrix = scorer.get_score_matrix(
        params.donors, params.recipients
    )
    if matchings_in_db is not None:
        all_solutions = matchings_in_db
    else:
        all_solutions = solver.solve(params.donors, params.recipients, scorer)

    matching_filter = filter_from_config(params.configuration)
    matchings_filtered = filter(matching_filter.keep, all_solutions)
    return list(matchings_filtered), score_matrix


if __name__ == "__main__":
    config = Configuration()
    solutions, score_matrix_main = solve_from_config(params=SolverInputParameters(
        donors=list(),
        recipients=list(),
        configuration=config
    ))
    logger.info(list(solutions))
