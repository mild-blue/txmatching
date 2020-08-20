from dataclasses import dataclass, field
from typing import List


@dataclass
class DonorRecipientScore:
    donor_id: int
    recipient_id: int
    score: float

# pylint: disable=too-many-instance-attributes
# I think it is reasonable to have many attributes here
@dataclass
class ConfigurationBase:
    scorer_constructor_name: str = "HLAAdditiveScorer"
    solver_constructor_name: str = "AllSolutionsSolver"
    enforce_compatible_blood_group: bool = False
    minimum_total_score: float = 0.0
    maximum_total_score: float = 27.0
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
MAN_DON_REC_SCORES = 'manual_donor_recipient_scores'
