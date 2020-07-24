from typing import List, Tuple, Dict

from kidney_exchange.database.services.patient_service import get_all_patients
from kidney_exchange.database.services.services_for_solve import db_matchings_to_matching_list
from kidney_exchange.database.sql_alchemy_schema import PairingResultModel
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.matching_with_score import MatchingWithScore
from kidney_exchange.solve_service.solve_from_db import solve_from_db
from kidney_exchange.utils.blood_groups import blood_groups_compatible

ScoreDict = Dict[Tuple[int, int], float]
BloodCompatibleDict = Dict[Tuple[int, int], bool]


def get_latest_matchings_and_score_matrix() -> Tuple[List[MatchingWithScore], ScoreDict, BloodCompatibleDict]:
    patients = get_all_patients()
    patients_dict = {patient.db_id: patient for patient in patients}

    donors_dict = {i: donor.db_id for i, donor in enumerate([donor for donor in patients if type(donor) == Donor])}
    recipients_dict = {i: recipient.db_id for i, recipient in
                       enumerate([recipient for recipient in patients if type(recipient) == Recipient])}

    last_pairing_result_model = PairingResultModel.query.order_by(PairingResultModel.updated_at.desc()).first()
    if last_pairing_result_model is None:
        solve_from_db()
        last_pairing_result_model = PairingResultModel.query.order_by(PairingResultModel.updated_at.desc()).first()
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
