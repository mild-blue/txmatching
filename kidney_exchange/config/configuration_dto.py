from dataclasses import dataclass
from typing import List

try:
    from kidney_exchange.config.configuration import RecipientDonorScore, Configuration
except ImportError:
    import sys

    RecipientDonorScore = sys.modules[__package__ + '.RecipientDonorScore']
    Configuration = sys.modules[__package__ + '.Configuration']


@dataclass
class RecipientDonorScoreDto:
    recipient_medical_id: str
    donor_medical_id: str
    compatibility_index: float


@dataclass
class ConfigurationDto:
    scorer_constructor_name: str
    solver_constructor_name: str
    enforce_same_blood_group: bool
    minimum_compatibility_index: float
    require_new_donor_having_better_match_in_compatibility_index: bool
    require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool
    use_binary_scoring: bool
    max_cycle_length: int
    max_sequence_length: int
    max_number_of_distinct_countries_in_round: int
    required_patient_ids: List[str]
    manual_recipient_donor_scores_dtos: List[RecipientDonorScoreDto]
