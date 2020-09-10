from typing import Dict, Iterator, List, Optional, Tuple

from dacite import from_dict

from txmatching.config.gives_superset_of_solutions import \
    gives_superset_of_solutions
from txmatching.database.services.config_service import (
    configuration_from_dict, get_config_models)
from txmatching.database.services.patient_service import (
    get_all_donors_recipients)
from txmatching.database.services.services_for_solve import (
    db_matchings_to_matching_list, get_pairing_result_for_config)
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.solve_service.data_objects.calculated_matchings import CalculatedMatchings
from txmatching.solve_service.data_objects.solver_input_parameters import \
    SolverInputParameters
from txmatching.solvers.matching.matching_with_score import \
    MatchingWithScore
from txmatching.utils.blood_groups import blood_groups_compatible

ScoreDict = Dict[Tuple[int, int], float]
BloodCompatibleDict = Dict[Tuple[int, int], bool]


def get_latest_matchings_and_score_matrix() -> Tuple[List[MatchingWithScore], ScoreDict, BloodCompatibleDict]:
    last_pairing_result_model = PairingResultModel.query.order_by(PairingResultModel.updated_at.desc()).first()

    if last_pairing_result_model is None:
        raise AssertionError('There are no latest matchings in the database, '
                             "didn't you forget to call solve_from_db()?")

    patients = get_all_donors_recipients()

    donors_dict = {donor.db_id: donor for donor in patients.donors}
    recipients_dict = {recipient.db_id: recipient for recipient in patients.recipients}

    calculated_matchings = from_dict(data_class=CalculatedMatchings,
                                     data=last_pairing_result_model.calculated_matchings)

    all_matchings = db_matchings_to_matching_list(calculated_matchings, donors_dict,
                                                  recipients_dict)

    all_matchings.sort(key=lambda matching: len(matching.get_rounds()), reverse=True)
    all_matchings.sort(key=lambda matching: matching.score(), reverse=True)
    all_matchings.sort(key=lambda matching: len(matching.donor_recipient_list), reverse=True)

    score_matrix = last_pairing_result_model.score_matrix['score_matrix_dto']
    score_dict = {
        (donor.db_id, recipient.db_id): score for donor, row in
        zip(patients.donors, score_matrix) for recipient, score in zip(patients.recipients, row)
    }

    compatible_blood_dict = {(donor.db_id, recipient.db_id): blood_groups_compatible(donor, recipient) for donor in
                             patients.donors for recipient in patients.recipients}

    return all_matchings, score_dict, compatible_blood_dict


def load_matching_for_config_from_db(exchange_parameters: SolverInputParameters) -> Optional[
    Iterator[MatchingWithScore]]:
    current_config = exchange_parameters.configuration

    compatible_config_models = list()
    for config_model in get_config_models():
        config_from_model = configuration_from_dict(config_model.parameters)
        if gives_superset_of_solutions(less_strict=config_from_model,
                                       more_strict=current_config):
            compatible_config_models.append(config_model)

    donors_dict = {donor.db_id: donor for donor in exchange_parameters.donors}
    recipients_dict = {recipient.db_id: recipient for recipient in exchange_parameters.recipients}

    for compatible_config in compatible_config_models:
        for pairing_result in get_pairing_result_for_config(compatible_config.id):
            calculated_matchings = from_dict(data_class=CalculatedMatchings, data=pairing_result.calculated_matchings)
            return db_matchings_to_matching_list(calculated_matchings, donors_dict, recipients_dict)

    return None
