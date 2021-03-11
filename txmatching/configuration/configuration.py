import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from txmatching.configuration.subclasses import (ForbiddenCountryCombination,
                                                 ManualDonorRecipientScore,
                                                 PatientDbId)
from txmatching.utils.country_enum import Country

DEFAULT_FORBIDDEN_COUNTRY_LIST = [ForbiddenCountryCombination(Country.AUT, Country.ISR),
                                  ForbiddenCountryCombination(Country.ISR, Country.AUT)]


class ComparisonMode(Enum):
    Smaller = 1
    Set = 2


COMPARISON_MODE = 'comparison_mode'


# pylint: disable=too-many-instance-attributes
# I think it is reasonable to have many attributes here
@dataclass
class Configuration:
    """
    Attributes:
    scorer_constructor_name: Scorer to use.
    solver_constructor_name: Solver to use.
    require_compatible_blood_group: If true, only AB0 compatible transplants are considered.
    minimum_total_score: Minimum total score (compatibility index + blood group bonus) that is required for
        a transplant to be possible.
    require_better_match_in_compatibility_index: If true, only transplants with better CI then the theoretical CI
        with the original donor.
    require_better_match_in_compatibility_index_or_blood_group: If true, only transplants with better CI then the
        theoretical CI with the original donor or AB0 compatible transplants are considered.
    blood_group_compatibility_bonus: Fixed constant (0) at the moment, could be updated in the future.
    use_binary_scoring: If all the conditions above are satisfied, then use just 1 for possible transplant
        and -inf for impossible.
    max_cycle_length: Number of patients in a cycle.
    max_sequence_length: Number of patients in a sequence.
    max_number_of_distinct_countries_in_round: Number of countries in a round.
    required_patient_db_ids: Only matchings with specified recipients are considered.
    use_high_resolution: Split codes are used for virtual crossmatch if true, broad otherwise.
    forbidden_country_combinations: Pairs of countries which do not support mutual transplantations.
    manual_donor_recipient_scores: Manual setting of score for tuple of recipient and donor.
    max_matchings_to_show_to_viewer: Viewer cannot see all the details of the app.
    max_number_of_matchings: Max matchings we keep in database and show to EDITOR.
    max_matchings_in_all_solutions_solver: Max allowed number of matchings all solutions solver searches for (to limit
     the duration of the computation)
    max_matchings_in_all_solutions_solver: Max allowed number of cycles all solutions solver searches for in the
    initial step of the comutation (to limit the duration of the computation)
    max_matchings_in_all_solutions_solver: Max allowed number of matchings ilp solver searches for (to limit
     the duration of the computation)
    """
    scorer_constructor_name: str = 'SplitHLAAdditiveScorer'
    solver_constructor_name: str = 'AllSolutionsSolver'
    require_compatible_blood_group: bool = False
    minimum_total_score: float = 0.0
    require_better_match_in_compatibility_index: bool = False
    require_better_match_in_compatibility_index_or_blood_group: bool = False
    blood_group_compatibility_bonus: float = 0.0
    use_binary_scoring: bool = False
    max_cycle_length: int = 4
    max_sequence_length: int = 4
    max_number_of_distinct_countries_in_round: int = 3
    required_patient_db_ids: List[PatientDbId] = field(default_factory=list,
                                                       metadata={COMPARISON_MODE: ComparisonMode.Set})
    use_high_resolution: bool = True
    forbidden_country_combinations: List[ForbiddenCountryCombination] = field(
        default_factory=lambda: DEFAULT_FORBIDDEN_COUNTRY_LIST,
        metadata={COMPARISON_MODE: ComparisonMode.Set})
    manual_donor_recipient_scores: List[ManualDonorRecipientScore] = field(
        default_factory=list,
        metadata={COMPARISON_MODE: ComparisonMode.Set}
    )
    max_debt_for_country: int = field(default=3,
                                      compare=True)
    max_matchings_to_show_to_viewer: int = field(default=5, compare=False)
    max_number_of_matchings: int = field(default=5,
                                         compare=True,
                                         metadata={COMPARISON_MODE: ComparisonMode.Smaller})
    max_matchings_in_all_solutions_solver: int = field(default=10000,
                                                       compare=True,
                                                       metadata={COMPARISON_MODE: ComparisonMode.Smaller})
    max_cycles_in_all_solutions_solver: int = field(default=1000000,
                                                    compare=True,
                                                    metadata={COMPARISON_MODE: ComparisonMode.Smaller})
    max_matchings_in_ilp_solver: int = field(default=20,
                                             compare=True,
                                             metadata={COMPARISON_MODE: ComparisonMode.Smaller})

    max_number_of_dynamic_constrains_ilp_solver: int = field(default=100,
                                                             compare=True,
                                                             metadata={COMPARISON_MODE: ComparisonMode.Smaller})

    def comparable(self, other):
        """
        Compare list fields as sets
        """
        for fld in dataclasses.fields(self):
            if fld.compare:
                val1 = getattr(self, fld.name, None)
                val2 = getattr(other, fld.name, None)

                if fld.metadata.get(COMPARISON_MODE, None) == ComparisonMode.Set:
                    if set(val1) != set(val2):
                        return False
                elif fld.metadata.get(COMPARISON_MODE, None) == ComparisonMode.Smaller:
                    if val1 > val2:
                        return False
                else:
                    if val1 != val2:
                        return False

        return True
