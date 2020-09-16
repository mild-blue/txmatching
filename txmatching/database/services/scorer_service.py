import dataclasses
from dataclasses import dataclass
from typing import List, Dict

from txmatching.database.services.config_service import get_current_configuration
from txmatching.database.services.patient_service import get_tx_session
from txmatching.scorers.additive_scorer import ScoreMatrix
from txmatching.scorers.scorer_from_config import scorer_from_configuration


@dataclass
class ScoreMatrixDto:
    score_matrix_dto: List


def score_matrix_to_dto(score_matrix: ScoreMatrix) -> Dict[str, Dict[str, ScoreMatrix]]:
    return dataclasses.asdict(ScoreMatrixDto(score_matrix))


def calculate_current_score_matrix() -> ScoreMatrix:
    configuration = get_current_configuration()
    scorer = scorer_from_configuration(configuration)
    patients = get_tx_session()
    score_matrix = scorer.get_score_matrix(patients.donors_dict, patients.recipients_dict)
    return score_matrix
