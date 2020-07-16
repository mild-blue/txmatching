import dataclasses
from dataclasses import dataclass, field
from typing import List, Dict

from kidney_exchange.database.services.patient_service import medical_id_to_db_id, db_id_to_medical_id

BOOL_KEYS_IN_CONFIG = [
    'enforce_compatible_blood_group',
    'require_new_donor_having_better_match_in_compatibility_index',
    'require_new_donor_having_better_match_in_compatibility_index_or_blood_group',
    'use_binary_scoring'
]

FLOAT_KEYS_IN_CONFIG = [
    'minimum_compatibility_index'
]

INT_KEYS_IN_CONFIG = [
    'max_cycle_length',
    'max_sequence_length',
    'max_number_of_distinct_countries_in_round'

]


@dataclass
class RecipientDonorScore:
    recipient_id: int
    donor_id: int
    compatibility_index: float


@dataclass
class RecipientDonorScoreDto:
    recipient_medical_id: str
    donor_medical_id: str
    compatibility_index: float


@dataclass
class Configuration:
    scorer_constructor_name: str = "HLAAdditiveScorer"
    solver_constructor_name: str = "AllSolutionsSolver"
    enforce_compatible_blood_group: bool = True
    minimum_compatibility_index: float = 0.0
    require_new_donor_having_better_match_in_compatibility_index: bool = True
    require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = True
    use_binary_scoring: bool = False
    max_cycle_length: int = 5
    max_sequence_length: int = 5
    max_number_of_distinct_countries_in_round: int = 2
    required_patient_db_ids: List[int] = field(default_factory=list)
    manual_recipient_donor_scores: List[RecipientDonorScore] = field(default_factory=list)


def rec_donor_score_from_dto(self: RecipientDonorScoreDto) -> RecipientDonorScore:
    return RecipientDonorScore(
        medical_id_to_db_id(self.recipient_medical_id),
        medical_id_to_db_id(self.donor_medical_id),
        self.compatibility_index
    )


def rec_donor_score_to_dto(self: RecipientDonorScore) -> RecipientDonorScoreDto:
    return RecipientDonorScoreDto(
        db_id_to_medical_id(self.recipient_id),
        db_id_to_medical_id(self.donor_id),
        self.compatibility_index
    )


def configuration_from_dto(configuration_dto: Dict) -> Configuration:
    configuration_dto = configuration_dto.copy()
    for bool_key in BOOL_KEYS_IN_CONFIG:
        if bool_key in configuration_dto:
            configuration_dto[bool_key] = True
        else:
            configuration_dto[bool_key] = False
    for int_key in INT_KEYS_IN_CONFIG:
        if int_key in configuration_dto:
            configuration_dto[int_key] = int(configuration_dto[int_key])
    for float_key in FLOAT_KEYS_IN_CONFIG:
        if float_key in configuration_dto:
            configuration_dto[float_key] = float(configuration_dto[float_key])

    configuration_dto["manual_recipient_donor_scores"] = [
        rec_donor_score_from_dto(rec_don_score) for rec_don_score in
        configuration_dto.pop("manual_recipient_donor_scores_dtos", [])]
    return Configuration(**configuration_dto)


def configuration_to_dto(configuration: Configuration) -> Dict:
    configuration_dto = dataclasses.asdict(configuration)
    configuration_dto["manual_recipient_donor_scores_dtos"] = [
        rec_donor_score_to_dto(rec_don_score) for rec_don_score in
        configuration_dto.pop("manual_recipient_donor_scores", [])]
    return configuration_dto
