from dataclasses import dataclass
from typing import List, Iterator, Optional

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.filters.filter_from_config import filter_from_config
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_from_config import scorer_from_config
from kidney_exchange.solvers.matching.matching import Matching
from kidney_exchange.solvers.solver_base import SolverBase
from kidney_exchange.solvers.solver_from_config import solver_from_config


@dataclass
class ExchangeParameters:
    donors: List[Donor]
    recipients: List[Recipient]
    configuration: Configuration


def solve_from_config(params: ExchangeParameters):
    scorer = scorer_from_config(params.configuration)
    solver = solver_from_config(params.configuration)
    matchings_in_db = load_matchings_from_database(params, solver)
    if matchings_in_db is not None:
        all_solutions = matchings_in_db
    else:
        all_solutions = solver.solve(params.donors, params.recipients, scorer)

    matching_filter = filter_from_config(params.configuration)
    return filter(matching_filter.keep, all_solutions)


def load_matchings_from_database(params: ExchangeParameters, solver: SolverBase) -> Optional[Iterator[Matching]]:
    breaking_param_dict = {}
    for breaking_param in solver.breaking_parameters()[params.configuration.scorer_constructor_name]:
        breaking_param_dict[breaking_param] = getattr(params.configuration, breaking_param)
    # TODO when database is ready, connect this to the database
    return None


if __name__ == "__main__":
    config = Configuration()
    solutions = list(solve_from_config(params=ExchangeParameters(
        donors=list(),
        recipients=list(),
        configuration=config
    )))
    print(solutions)
