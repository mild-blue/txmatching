import ast
import logging
from typing import Union, Dict

from kidney_exchange.config.configuration import Configuration, DonorRecipientScore, MAN_DON_REC_SCORES, \
    BOOL_KEYS_IN_CONFIG, INT_KEYS_IN_CONFIG, FLOAT_KEYS_IN_CONFIG
from kidney_exchange.data_transfer_objects.configuration.configuration_dto import MAN_DON_REC_SCORES_DTO
from kidney_exchange.database.services.patient_service import medical_id_to_db_id
from kidney_exchange.scorers.additive_scorer import TRANSPLANT_IMPOSSIBLE

logger = logging.getLogger(__name__)


def _score_from_dto(score: float) -> Union[float, str]:
    if type(score) == int or type(score) == float:
        if score == -1:
            return TRANSPLANT_IMPOSSIBLE
        elif score < 0:
            raise ValueError("Score cannot be smaller than 0")
        else:
            return score
    else:
        raise ValueError(f"Unexpected format of {score}")


def configuration_from_dto(configuration_dto: Dict) -> Configuration:
    configuration = configuration_dto.copy()
    try:
        possible_man = configuration.pop(MAN_DON_REC_SCORES_DTO, '[]')
        if possible_man == '':
            possible_man = '[]'
        score_dtos = ast.literal_eval(possible_man)
        scores = []
        for score_tuple in score_dtos:
            scores.append(DonorRecipientScore(
                donor_id=medical_id_to_db_id(score_tuple[0]),
                recipient_id=medical_id_to_db_id(score_tuple[1]),
                score=_score_from_dto(score_tuple[2])
            ))
        configuration[MAN_DON_REC_SCORES] = scores

    except (ValueError, IndexError, SyntaxError) as e:
        logger.error(f"could not process {MAN_DON_REC_SCORES_DTO}: {e}")
        configuration[MAN_DON_REC_SCORES] = []
        pass
    for bool_key in BOOL_KEYS_IN_CONFIG:
        if bool_key in configuration:
            configuration[bool_key] = True
        else:
            configuration[bool_key] = False
    for int_key in INT_KEYS_IN_CONFIG:
        if int_key in configuration:
            configuration[int_key] = int(configuration[int_key])
    for float_key in FLOAT_KEYS_IN_CONFIG:
        if float_key in configuration:
            configuration[float_key] = float(configuration[float_key])

    return Configuration(**configuration)
