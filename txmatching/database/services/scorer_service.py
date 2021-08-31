import dataclasses
from dataclasses import dataclass
from typing import Dict, List

from dacite import from_dict

from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel
from txmatching.scorers.additive_scorer import ScoreMatrix


@dataclass
class ScoreMatrixDto:
    score_matrix_dto: List[List[float]]


def score_matrix_to_dict(score_matrix: ScoreMatrix) -> Dict[str, List[List[float]]]:
    return dataclasses.asdict(ScoreMatrixDto(score_matrix.tolist()))


def score_matrix_from_dict(score_matrix_dict: Dict[str, List[List[float]]]) -> List[List[float]]:
    score_matrix_dto = from_dict(data_class=ScoreMatrixDto, data=score_matrix_dict)
    return score_matrix_dto.score_matrix_dto


def matchings_model_from_dict(calculated_matchings_dict: Dict[str, any]) -> MatchingsModel:
    return from_dict(data_class=MatchingsModel,
                     data=calculated_matchings_dict)
