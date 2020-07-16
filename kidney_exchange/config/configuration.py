import ast
import dataclasses
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Union

from kidney_exchange.database.services.patient_service import medical_id_to_db_id, db_id_to_medical_id
from kidney_exchange.scorers.scorer_constants import TRANSPLANT_IMPOSSIBLE

logger = logging.getLogger(__name__)

BOOL_KEYS_IN_CONFIG = [
    'enforce_compatible_blood_group',
    'require_new_donor_having_better_match_in_compatibility_index',
    'require_new_donor_having_better_match_in_compatibility_index_or_blood_group',
    'use_binary_scoring'
]

FLOAT_KEYS_IN_CONFIG = [
    'minimum_total_score'
]

INT_KEYS_IN_CONFIG = [
    'max_cycle_length',
    'max_sequence_length',
    'max_number_of_distinct_countries_in_round'

]

MAN_REC_DON_SCORES = 'manual_donor_recipient_scores'
MAN_REC_DON_SCORES_DTO = 'manual_donor_recipient_scores_dto'


@dataclass
class DonorRecipientScore:
    donor_id: int
    recipient_id: int
    score: float


@dataclass
class DonorRecipientScoreDto:
    donor_medical_id: str
    recipient_medical_id: str
    score: float


@dataclass
class ConfigurationBase:
    scorer_constructor_name: str = "HLAAdditiveScorer"
    solver_constructor_name: str = "AllSolutionsSolver"
    enforce_compatible_blood_group: bool = False
    minimum_total_score: float = 0.0
    require_new_donor_having_better_match_in_compatibility_index: bool = False
    require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = False
    use_binary_scoring: bool = False
    max_cycle_length: int = 100
    max_sequence_length: int = 100
    max_number_of_distinct_countries_in_round: int = 100
    required_patient_db_ids: List[int] = field(default_factory=list)


@dataclass
class Configuration(ConfigurationBase):
    manual_donor_recipient_scores: List[DonorRecipientScore] = field(default_factory=list)


@dataclass
class ConfigurationDto(Configuration):
    manual_donor_recipient_scores_dto: List[Tuple[str, str, float]] = field(default_factory=list)


def rec_donor_score_to_dto(self: DonorRecipientScore) -> Tuple[str, str, float]:
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
        possible_man = configuration.pop(MAN_REC_DON_SCORES_DTO, '[]')
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
        configuration[MAN_REC_DON_SCORES] = scores

    except (ValueError, IndexError, SyntaxError) as e:
        logger.error(f"could not process {MAN_REC_DON_SCORES_DTO}: {e}")
        configuration[MAN_REC_DON_SCORES] = []
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


def configuration_to_dto(configuration: Configuration) -> ConfigurationDto:
    configuration_dto = dataclasses.asdict(configuration)
    configuration_dto[MAN_REC_DON_SCORES_DTO] = [
        rec_donor_score_to_dto(rec_don_score) for rec_don_score in
        configuration.manual_donor_recipient_scores]
    del configuration_dto[MAN_REC_DON_SCORES]

    return ConfigurationDto(**configuration_dto)
