import dataclasses
from dataclasses import dataclass
from typing import List

import numpy as np

from kidney_exchange.database.services.config_service import get_current_configuration
from kidney_exchange.database.services.patient_service import get_donors_recipients_from_db
from kidney_exchange.scorers.scorer_from_config import scorer_from_configuration


@dataclass
class ScoreMatrix:
    score_matrix_dto: List[List[float]]


def score_matrix_to_dto(score_matrix):
    # TODO should we save the matrix? Is there any point? There is issue with np.nan anyway..
    return dataclasses.asdict(ScoreMatrix(np.nan_to_num(score_matrix).tolist()))


def calculate_current_score_matrix():
    configuration = get_current_configuration()
    scorer = scorer_from_configuration(configuration)
    donors, recipients = get_donors_recipients_from_db()
    score_matrix = scorer.get_score_matrix(donors, recipients)

    return score_matrix_to_dto(score_matrix)
