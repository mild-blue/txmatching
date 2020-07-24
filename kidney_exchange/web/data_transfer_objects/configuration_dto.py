import ast
import dataclasses
import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Union, Dict

from kidney_exchange.config.configuration import Configuration, DonorRecipientScore, BOOL_KEYS_IN_CONFIG, \
    FLOAT_KEYS_IN_CONFIG, INT_KEYS_IN_CONFIG, MAN_DON_REC_SCORES
from kidney_exchange.database.services.patient_service import db_id_to_medical_id, medical_id_to_db_id
from kidney_exchange.scorers.scorer_constants import TRANSPLANT_IMPOSSIBLE

logger = logging.getLogger(__name__)


@dataclass
class DonorRecipientScoreDTO:
    donor_medical_id: str
    recipient_medical_id: str
    score: float


@dataclass
class ConfigurationDTO(Configuration):
    manual_donor_recipient_scores_dto: List[Tuple[str, str, float]] = field(default_factory=list)


MAN_DON_REC_SCORES_DTO = 'manual_donor_recipient_scores_dto'


def donor_recipient_score_to_dto(self: DonorRecipientScore) -> Tuple[str, str, float]:
    return (
        db_id_to_medical_id(self.donor_id),
        db_id_to_medical_id(self.recipient_id),
        score_to_dto(self.score)
    )


def score_to_dto(score: Union[float, str]) -> float:
    if type(score) == int or type(score) == float:
        return score
    else:
        return -1


def score_from_dto(score: float) -> Union[float, str]:
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
                score=score_from_dto(score_tuple[2])
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


def configuration_to_dto(configuration: Configuration) -> ConfigurationDTO:
    configuration_dto = dataclasses.asdict(configuration)
    configuration_dto[MAN_DON_REC_SCORES_DTO] = [
        donor_recipient_score_to_dto(don_rec_score) for don_rec_score in
        configuration.manual_donor_recipient_scores]
    del configuration_dto[MAN_DON_REC_SCORES]

    return ConfigurationDTO(**configuration_dto)
