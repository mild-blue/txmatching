import dataclasses
from dataclasses import dataclass, field
from typing import List

from txmatching.configuration.subclasses import (ForbiddenCountryCombination,
                                                 ManualDonorRecipientScore,
                                                 PatientDbId)
from txmatching.utils.country_enum import Country

DEFAULT_FORBIDDEN_COUNTRY_LIST = [ForbiddenCountryCombination(Country.AUT, Country.ISR),
                                  ForbiddenCountryCombination(Country.ISR, Country.AUT)]


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
    maximum_total_score: Fixed constant at the moment.
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
    use_split_resolution: Split codes are used for virtual crossmatch if true, broad otherwise.
    forbidden_country_combinations: Pairs of countries which do not support mutual transplantations.
    manual_donor_recipient_scores: Manual setting of score for tuple of recipient and donor.
    max_matchings_to_show_to_viewer: Viewer cannot see all the details of the app.
    max_matchings_to_show_to_store_in_db: Max matchings we keep in database and show to EDITOR.
    max_allowed_number_of_matchings: Max allowed number of matchings the user is allowed to work with.
    """
    scorer_constructor_name: str = 'HLAAdditiveScorer'
    solver_constructor_name: str = 'AllSolutionsSolver'
    require_compatible_blood_group: bool = False
    minimum_total_score: float = 0.0
    maximum_total_score: float = 26.0
    require_better_match_in_compatibility_index: bool = False
    require_better_match_in_compatibility_index_or_blood_group: bool = False
    blood_group_compatibility_bonus: float = 0.0
    use_binary_scoring: bool = False
    max_cycle_length: int = 4
    max_sequence_length: int = 4
    max_number_of_distinct_countries_in_round: int = 3
    # For equality comparison, the field bellow is treated as set (see __eq__() function)
    # TODO: https://github.com/mild-blue/txmatching/issues/373 change field type to set
    required_patient_db_ids: List[PatientDbId] = field(default_factory=list)
    use_split_resolution: bool = True
    # For equality comparison, the field bellow is treated as set (see __eq__() function)
    # TODO: https://github.com/mild-blue/txmatching/issues/373 change field type to set
    forbidden_country_combinations: List[ForbiddenCountryCombination] = field(
        default_factory=lambda: DEFAULT_FORBIDDEN_COUNTRY_LIST)
    # For equality comparison, the field bellow is treated as set (see __eq__() function)
    # TODO: https://github.com/mild-blue/txmatching/issues/373 change field type to set
    manual_donor_recipient_scores: List[ManualDonorRecipientScore] = field(default_factory=list)
    max_matchings_to_show_to_viewer: int = field(default=10, compare=False)
    max_matchings_to_store_in_db: int = field(default=100, compare=False)
    max_allowed_number_of_matchings: int = field(default=10000, compare=False)
    max_allowed_number_of_cycles_to_be_searched: int = field(default=10000000, compare=False)

    def __eq__(self, other):
        """
        Compare list fields as sets
        """
        fields = getattr(self, dataclasses._FIELDS, None)

        for fld in fields.values():
            if fld._field_type is not dataclasses._FIELD or not fld.compare:
                continue

            val1 = getattr(self, fld.name, None)
            val2 = getattr(other, fld.name, None)

            if fld.name in [
                'required_patient_db_ids',
                'forbidden_country_combinations',
                'manual_donor_recipient_scores',
            ]:
                if set(val1) != set(val2):
                    return False
            elif val1 != val2:
                return False

        return True
