import logging
from typing import Iterator, Optional, Iterable, Tuple

import numpy as np

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.config.gives_superset_of_solutions import gives_superset_of_solutions
from kidney_exchange.database.services.config_service import get_config_models, config_model_to_configuration
from kidney_exchange.database.services.patient_service import medical_id_to_db_id
from kidney_exchange.database.services.services_for_solve import get_pairing_result_for_config, \
    get_patients_for_pairing_result, \
    db_matchings_to_matching_list
from kidney_exchange.filters.filter_from_config import filter_from_config
from kidney_exchange.scorers.scorer_from_config import scorer_from_configuration
from kidney_exchange.solve_service.data_objects.solver_input_parameters import SolverInputParameters
from kidney_exchange.solvers.matching.matching_with_score import MatchingWithScore
from kidney_exchange.solvers.solver_from_config import solver_from_config

logger = logging.getLogger(__name__)


def solve_from_config(params: SolverInputParameters) -> Tuple[Iterable[MatchingWithScore], np.array]:
    scorer = scorer_from_configuration(params.configuration)
    solver = solver_from_config(params.configuration)
    matchings_in_db = _load_matchings_from_database(params)
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


def _load_matchings_from_database(exchange_parameters: SolverInputParameters) -> Optional[Iterator[MatchingWithScore]]:
    current_config = exchange_parameters.configuration

    compatible_config_models = list()
    for config_model in get_config_models():
        config_from_model = config_model_to_configuration(config_model)
        if gives_superset_of_solutions(less_strict=config_from_model,
                                       more_strict=current_config):
            compatible_config_models.append(config_model)

    current_patient_ids = {medical_id_to_db_id(patient.medical_id) for patient in
                           exchange_parameters.donors + exchange_parameters.recipients}

    patients_dict = {patient.db_id: patient for patient in exchange_parameters.donors + exchange_parameters.recipients}

    for compatible_config in compatible_config_models:
        for pairing_result in get_pairing_result_for_config(compatible_config.id):
            compatible_config_patient_ids = {p.patient_id for p in get_patients_for_pairing_result(pairing_result.id)}
            if compatible_config_patient_ids == current_patient_ids:
                return db_matchings_to_matching_list(pairing_result.calculated_matchings, patients_dict)

    return None


if __name__ == "__main__":
    config = Configuration()
    solutions, score_matrix_main = solve_from_config(params=SolverInputParameters(
        donors=list(),
        recipients=list(),
        configuration=config
    ))
    logger.info(list(solutions))
