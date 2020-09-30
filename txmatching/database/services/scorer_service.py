import dataclasses
from dataclasses import dataclass
from typing import Dict, List

from txmatching.configuration.configuration import Configuration
from txmatching.database.services.patient_service import get_txm_event
from txmatching.scorers.additive_scorer import ScoreMatrix
from txmatching.scorers.scorer_from_config import scorer_from_configuration


@dataclass
class ScoreMatrixDto:
    score_matrix_dto: List


def score_matrix_to_dto(score_matrix: ScoreMatrix) -> Dict[str, Dict[str, ScoreMatrix]]:
    return dataclasses.asdict(ScoreMatrixDto(score_matrix))


def calculate_current_score_matrix(configuration: Configuration, txm_event_db_id: int) -> ScoreMatrix:
    scorer = scorer_from_configuration(configuration)
    patients = get_txm_event(txm_event_db_id)
    score_matrix = scorer.get_score_matrix(patients.donors_dict, patients.recipients_dict)
    return score_matrix
