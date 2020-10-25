import dataclasses
from dataclasses import dataclass
from typing import Dict, List

from txmatching.scorers.additive_scorer import ScoreMatrix


@dataclass
class ScoreMatrixDto:
    score_matrix_dto: List[List[float]]


def score_matrix_to_dto(score_matrix: ScoreMatrix) -> Dict[str, Dict[str, ScoreMatrix]]:
    return dataclasses.asdict(ScoreMatrixDto(score_matrix.tolist()))
