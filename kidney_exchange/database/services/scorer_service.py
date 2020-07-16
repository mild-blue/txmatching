import dataclasses
from dataclasses import dataclass
from typing import List, Dict

from kidney_exchange.database.services.config_service import get_current_configuration
from kidney_exchange.database.services.patient_service import get_donors_recipients_from_db
from kidney_exchange.scorers.additive_scorer import ScoreMatrix
from kidney_exchange.scorers.scorer_from_config import scorer_from_configuration


@dataclass
class ScoreMatrixDto:
    score_matrix_dto: List


def score_matrix_to_dto(score_matrix: ScoreMatrix) -> Dict[str, Dict[str, ScoreMatrix]]:
    return dataclasses.asdict(ScoreMatrixDto(score_matrix))


def calculate_current_score_matrix() -> ScoreMatrix:
    configuration = get_current_configuration()
    scorer = scorer_from_configuration(configuration)
    donors, recipients = get_donors_recipients_from_db()
    score_matrix = scorer.get_score_matrix(donors, recipients)
    return score_matrix
