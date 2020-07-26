from typing import List, Tuple, Dict, Optional, Iterator

from kidney_exchange.config.gives_superset_of_solutions import gives_superset_of_solutions
from kidney_exchange.database.services.config_service import get_config_models, config_model_to_configuration
from kidney_exchange.database.services.patient_service import get_all_patients, medical_id_to_db_id
from kidney_exchange.database.services.services_for_solve import db_matchings_to_matching_list, \
    get_pairing_result_for_config, get_patients_for_pairing_result
from kidney_exchange.database.sql_alchemy_schema import PairingResultModel
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solve_service.data_objects.solver_input_parameters import SolverInputParameters
from kidney_exchange.solvers.matching.matching_with_score import MatchingWithScore
from kidney_exchange.utils.blood_groups import blood_groups_compatible

ScoreDict = Dict[Tuple[int, int], float]
BloodCompatibleDict = Dict[Tuple[int, int], bool]


def get_latest_matchings_and_score_matrix() -> Tuple[List[MatchingWithScore], ScoreDict, BloodCompatibleDict]:
    last_pairing_result_model = PairingResultModel.query.order_by(PairingResultModel.updated_at.desc()).first()

    if last_pairing_result_model is None:
        raise AssertionError("There are no latest matchings in the database, "
                             "didn't you forget to call solve_from_db()?")

    patients = get_all_patients()
    patients_dict = {patient.db_id: patient for patient in patients}

    donors_dict = {i: donor.db_id for i, donor in enumerate([donor for donor in patients if type(donor) == Donor])}
    recipients_dict = {i: recipient.db_id for i, recipient in
                       enumerate([recipient for recipient in patients if type(recipient) == Recipient])}

    all_matchings = db_matchings_to_matching_list(last_pairing_result_model.calculated_matchings, patients_dict)

    all_matchings.sort(key=lambda matching: len(matching.get_rounds()), reverse=True)
    all_matchings.sort(key=lambda matching: matching.score(), reverse=True)
    all_matchings.sort(key=lambda matching: len(matching.donor_recipient_list), reverse=True)

    score_matrix = last_pairing_result_model.score_matrix["score_matrix_dto"]
    score_dict = {
        (donors_dict[donor_index], recipients_dict[recipient_index]): score for donor_index, row in
        enumerate(score_matrix) for recipient_index, score in enumerate(row)
    }

    compatible_blood_dict = {(donor.db_id, recipient.db_id): blood_groups_compatible(donor, recipient) for donor in
                             patients if type(donor) == Donor for recipient in patients if type(recipient) == Recipient}

    return all_matchings, score_dict, compatible_blood_dict


def load_matchings_from_database(exchange_parameters: SolverInputParameters) -> Optional[Iterator[MatchingWithScore]]:
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
