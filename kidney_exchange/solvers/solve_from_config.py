from dataclasses import dataclass
from typing import List, Iterator, Optional

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.config.gives_superset_of_solutions import gives_superset_of_solutions
from kidney_exchange.database.services.matching import get_pairing_result_for_config, get_patients_for_pairing_result, \
    db_matching_to_matching, get_latest_configuration, \
    get_donor_from_db, get_recipient_from_db, medical_id_to_id, config_model_to_config, get_config_models, \
    get_all_patients
from kidney_exchange.filters.filter_from_config import filter_from_config
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_from_config import scorer_from_config
from kidney_exchange.solvers.matching.matching import Matching
from kidney_exchange.solvers.solver_from_config import solver_from_config


@dataclass
class ExchangeParameters:
    donors: List[Donor]
    recipients: List[Recipient]
    configuration: Configuration


def solve_from_db():
    patients = get_all_patients()
    # TODO dont use strings here, use some better logic (ENUMS for example)
    # https://trello.com/c/pKMqnv7X
    donors = [get_donor_from_db(don.id) for don in patients if don.patient_type == 'DONOR']
    recipients = [get_recipient_from_db(rec.id) for rec in patients if rec.patient_type == 'RECIPIENT']
    final_solutions = solve_from_config(ExchangeParameters(
        donors=donors,
        recipients=recipients,
        configuration=get_latest_configuration()
    ))
    return list(final_solutions)


def solve_from_config(params: ExchangeParameters):
    scorer = scorer_from_config(params.configuration)
    solver = solver_from_config(params.configuration)
    matchings_in_db = load_matchings_from_database(params)
    if matchings_in_db is not None:
        all_solutions = matchings_in_db
    else:
        all_solutions = solver.solve(params.donors, params.recipients, scorer)

    matching_filter = filter_from_config(params.configuration)
    return filter(matching_filter.keep, all_solutions)


def load_matchings_from_database(exchange_parameters: ExchangeParameters) -> Optional[Iterator[Matching]]:
    current_config = exchange_parameters.configuration

    compatible_config_models = list()
    for config_model in get_config_models():
        config_from_model = config_model_to_config(config_model)
        if gives_superset_of_solutions(less_strict=config_from_model,
                                       more_strict=current_config):
            compatible_config_models.append(config_model)

    current_patient_ids = {medical_id_to_id(patient.patient_id) for patient in
                           exchange_parameters.donors + exchange_parameters.recipients}

    for compatible_config in compatible_config_models:
        for pairing_result in get_pairing_result_for_config(compatible_config.id):
            compatible_config_patient_ids = {p.patient_id for p in get_patients_for_pairing_result(pairing_result.id)}
            if compatible_config_patient_ids == current_patient_ids:
                return db_matching_to_matching(pairing_result.calculated_matchings)

    return None


if __name__ == "__main__":
    config = Configuration()
    solutions = list(solve_from_config(params=ExchangeParameters(
        donors=list(),
        recipients=list(),
        configuration=config
    )))
    print(solutions)
