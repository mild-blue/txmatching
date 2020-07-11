from dataclasses import dataclass, field
from typing import List


@dataclass
class Configuration:
    scorer_constructor_name: str = "HLAAdditiveScorer"
    solver_constructor_name: str = "AllSolutionsSolver"
    enforce_same_blood_group: bool = True
    minimum_compatibility_index: float = 0.0
    require_new_donor_having_better_match_in_compatibility_index: bool = True
    require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = True
    use_binary_scoring: bool = False
    max_cycle_length: int = 5
    max_sequence_length: int = 5
    max_number_of_distinct_countries_in_round: int = 2
    required_patient_ids: List[str] = field(default_factory=list)
