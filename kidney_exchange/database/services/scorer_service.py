import numpy as np

from kidney_exchange.database.db import db
from kidney_exchange.database.services.config_service import get_current_configuration
from kidney_exchange.database.services.patient_service import get_donors_recipients_from_db
from kidney_exchange.database.sql_alchemy_schema import PairingResultModel, PairingResultPatientModel
from kidney_exchange.scorers.scorer_from_config import scorer_from_configuration


def calculate_and_save_current_score_matrix():
    configuration = get_current_configuration()
    scorer = scorer_from_configuration(configuration)
    donors, recipients = get_donors_recipients_from_db()
    score_matrix = scorer.get_score_matrix(donors, recipients)
    patient_ids = [PairingResultPatientModel(patient_id=patient.db_id) for patient in donors + recipients]
    score_matrix_for_db = PairingResultModel(
        config_id=0,
        patients=patient_ids,
        id=0,
        score_matrix={
            "score_matrix": score_matrix.tolist()
        },
        calculated_matchings={},
        valid=True
    )
    maybe_pairing_result = PairingResultModel.query.get(0)
    if maybe_pairing_result is not None:
        maybe_pairing_result.delete()
    db.session.commit()

    db.session.add(score_matrix_for_db)
    db.session.commit()
    return score_matrix_for_db.id


def get_current_score_matrix():
    current_score_matrix = PairingResultModel.query.get(0)
    if current_score_matrix is None:
        calculate_and_save_current_score_matrix()
        current_score_matrix = PairingResultModel.query.get(0)
    score_matrix = np.array(current_score_matrix.score_matrix["score_matrix"])
    return score_matrix
