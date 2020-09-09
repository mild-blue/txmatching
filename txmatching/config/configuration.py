from dataclasses import dataclass, field
from typing import List, Tuple

from txmatching.utils.country import Country

DEFAULT_FORBIDDEN_COUNTRY_LIST = [(Country.AUT, Country.IL), (Country.IL, Country.AUT)]


@dataclass
class DonorRecipientScore:
    donor_id: int
    recipient_id: int
    score: float


# pylint: disable=too-many-instance-attributes
# I think it is reasonable to have many attributes here

@dataclass
class ConfigurationBase:
    """
    Attributes:
        minimum_total_score: Minimum total score (compatibility index + blood group bonus) that is required for
        a transplant to be possible
        use_binary_scoring: If all the conditions above are satisfied, then use just 1 for possible transplant
        and -inf for impossible
    """
    scorer_constructor_name: str = "HLAAdditiveScorer"
    solver_constructor_name: str = "AllSolutionsSolver"
    enforce_compatible_blood_group: bool = False
    minimum_total_score: float = 0.0
    maximum_total_score: float = 27.0
    require_new_donor_having_better_match_in_compatibility_index: bool = False
    require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = False
    blood_group_compatibility_bonus = 0.0
    forbidden_country_combinations: List[Tuple[Country, Country]] = field(
        default_factory=lambda: DEFAULT_FORBIDDEN_COUNTRY_LIST)
    use_binary_scoring: bool = False
    max_cycle_length: int = 100
    max_sequence_length: int = 100
    max_number_of_distinct_countries_in_round: int = 100
    required_patient_db_ids: List[int] = field(default_factory=list)
    allow_low_high_res_incompatible: bool = False


@dataclass
class Configuration(ConfigurationBase):
    """
    Attributes:
         manual_donor_recipient_scores: Manual setting of score for tuple of recipient and donor
     """
    manual_donor_recipient_scores: List[DonorRecipientScore] = field(default_factory=list)


# TODO process correctly forbidden_country_combinations and allow_low_high_res_incompatible
BOOL_KEYS_IN_CONFIG = [
    'enforce_compatible_blood_group',
    'require_new_donor_having_better_match_in_compatibility_index',
    'require_new_donor_having_better_match_in_compatibility_index_or_blood_group',
    'use_binary_scoring',
    'allow_low_high_res_incompatible'
]
FLOAT_KEYS_IN_CONFIG = [
    'minimum_total_score',
    'blood_group_compatibility_bonus'
]
INT_KEYS_IN_CONFIG = [
    'max_cycle_length',
    'max_sequence_length',
    'max_number_of_distinct_countries_in_round'

]
MAN_DON_REC_SCORES = 'manual_donor_recipient_scores'
