from dataclasses import dataclass
from typing import List, Iterator, Optional

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.database.services.matching import get_configs_compatible_with_params, \
    get_pairing_result_for_config, get_patients_for_pairing_result, db_matching_to_matching, get_latest_configuration, \
    get_donor_from_db, get_recipient_from_db, medical_id_to_id
from kidney_exchange.database.sql_alchemy_schema import PatientModel
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


def solve_from_db():
    pats = PatientModel.query.all()
    donors = [get_donor_from_db(don.id) for don in pats if don.patient_type == 'DONOR']
    recipients = [get_recipient_from_db(rec.id) for rec in pats if rec.patient_type == 'RECIPIENT']
    return list(solve_from_config(ExchangeParameters(
        donors=donors,
        recipients=recipients,
        configuration=get_latest_configuration()
    )))


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
    new_patients = {medical_id_to_id(d.patient_id) for d in params.donors}.union(
        {medical_id_to_id(r.patient_id) for r in params.recipients})

    compatible_configs = get_configs_compatible_with_params(breaking_param_dict)
    for compatible_config in compatible_configs:
        for pairing_result in get_pairing_result_for_config(compatible_config.id):
            old_patients = {p.patient_id for p in get_patients_for_pairing_result(pairing_result.id)}
            if old_patients == new_patients:
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
