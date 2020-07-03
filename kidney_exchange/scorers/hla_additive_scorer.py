from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.additive_scorer import AdditiveScorer


class HLAAdditiveScorer(AdditiveScorer):
    def __init__(self, enforce_same_blood_group: bool = True,
                 minimum_compatibility_index: float = 0.0,
                 require_new_donor_having_better_match_in_blood_group: bool = True,
                 require_new_donor_having_better_match_in_compatibility_index: bool = True,
                 use_binary_scoring: bool = False):
        """
        :param enforce_same_blood_group:
            True: donor has to have the same blood group as recipient
            False: donor just needs to have blood group that is in recipients acceptable blood groups
        :param minimum_compatibility_index: Minimum index of compatibility that is required for a transplant
        :param require_new_donor_having_better_match_in_blood_group: New donor for recipient needs to have a better
            match in blood group than (the best of) his original relative(s)
        :param require_new_donor_having_better_match_in_compatibility_index: New donor for recipient needs to have
            a better match in the compatibility index than (the best of) his original relative(s)
        :param use_binary_scoring: If all the conditions above are satisfied, then use just 1 for possible transplant
            and -inf for impossible
        """
        self._enforce_same_blood = enforce_same_blood_group
        self._minimum_compatibility_index = minimum_compatibility_index
        self._require_new_donor_having_better_match_in_blood_group = require_new_donor_having_better_match_in_blood_group
        self._require_new_donor_having_better_match_in_compatibility_index = require_new_donor_having_better_match_in_compatibility_index
        self._use_binary_scoring = use_binary_scoring

    def _score_transplant(self, donor: Donor, recipient: Recipient) -> float:
        raise NotImplementedError("TODO: Implement")  # TODO: Implement
