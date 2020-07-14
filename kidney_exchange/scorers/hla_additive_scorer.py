from typing import List

from kidney_exchange.config.configuration import Configuration, RecipientDonorScore
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.additive_scorer import AdditiveScorer, TRANSPLANT_IMPOSSIBLE
from kidney_exchange.utils.blood_groups import blood_groups_compatible
from kidney_exchange.utils.hla_system.compatibility_index import compatibility_index

BLOOD_GROUP_COMPATIBILITY_BONUS = 0.5


class HLAAdditiveScorer(AdditiveScorer):
    def __init__(self, recipient_donor_scores: List[RecipientDonorScore] = None,
                 enforce_compatible_blood_group: bool = True,
                 minimum_compatibility_index: float = 0.0,
                 require_new_donor_having_better_match_in_compatibility_index: bool = True,
                 require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = True,
                 use_binary_scoring: bool = False):
        """
        :param recipient_donor_scores:
            Manual setting of score for tuple of recipient and donor
        :param enforce_compatible_blood_group:
            True: donor has to have the compatible blood group with the recipient
            False: donor just needs to have blood group that is in recipients acceptable blood groups
        :param minimum_compatibility_index: Minimum index of compatibility that is required for a transplant to be possible
        :param require_new_donor_having_better_match_in_compatibility_index: New donor for recipient needs to have
            a better match in the compatibility index than (the best of) his original relative(s)
        :param require_new_donor_having_better_match_in_compatibility_index_or_blood_group: New donor for recipient needs
            to have a better match in compatibility index or in blood group than (the best of) his original relative(s)
        :param use_binary_scoring: If all the conditions above are satisfied, then use just 1 for possible transplant
            and -inf for impossible
        """
        super().__init__(recipient_donor_scores)
        self._enforce_compatible_blood = enforce_compatible_blood_group
        self._minimum_compatibility_index = minimum_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index = require_new_donor_having_better_match_in_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group = require_new_donor_having_better_match_in_compatibility_index_or_blood_group
        self._use_binary_scoring = use_binary_scoring

    def score_transplant_calculated(self, donor: Donor, recipient: Recipient) -> float:
        donor_recipient_ci = compatibility_index(donor.parameters, recipient.parameters)
        related_donor_recipient_ci = compatibility_index(recipient.related_donor.parameters, recipient.parameters)

        # Donor must have blood group that is acceptable for recipient
        if donor.parameters.blood_group not in recipient.parameters.acceptable_blood_groups:
            return TRANSPLANT_IMPOSSIBLE

        # Recipient can't have antibodies that donor has antigens for
        # TODO: Ask immunologists what is exactly the bad combination and for what antigens?
        for antibody_code in recipient.parameters.hla_antibodies.codes + recipient.parameters.hla_antibodies_low_resolution:
            if antibody_code in donor.parameters.hla_antigens.codes + donor.parameters.hla_antigens_low_resolution:
                return TRANSPLANT_IMPOSSIBLE

        # If required, donor must have either better match in blood group or better compatibility index than
        # the donor related to the recipient
        if self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group \
                and (donor.parameters.blood_group != recipient.parameters.blood_group
                     and donor_recipient_ci <= related_donor_recipient_ci):
            return TRANSPLANT_IMPOSSIBLE

        # If required, the donor must have the compatible blood group with recipient
        if self._enforce_compatible_blood and not blood_groups_compatible(donor, recipient):
            return TRANSPLANT_IMPOSSIBLE

        # If required, the compatibility index between donor and recipient must be higher than
        # between recipient and the donor related to him
        if self._require_new_donor_having_better_match_in_compatibility_index \
                and donor_recipient_ci <= related_donor_recipient_ci:
            return TRANSPLANT_IMPOSSIBLE

        # The compatibility index must be higher than the minimum required
        if donor_recipient_ci < self._minimum_compatibility_index:
            return TRANSPLANT_IMPOSSIBLE

        if self._use_binary_scoring:
            return 1.0
        else:
            blood_group_bonus = self._blood_group_bonus(donor, recipient)
            return donor_recipient_ci + blood_group_bonus

    @classmethod
    def from_config(cls, configuration: Configuration) -> "HLAAdditiveScorer":
        hla_additive_scorer = HLAAdditiveScorer(
            recipient_donor_scores=configuration.manual_recipient_donor_scores,
            enforce_compatible_blood_group=configuration.enforce_compatible_blood_group,
            minimum_compatibility_index=configuration.minimum_compatibility_index,
            require_new_donor_having_better_match_in_compatibility_index=configuration.require_new_donor_having_better_match_in_compatibility_index,
            require_new_donor_having_better_match_in_compatibility_index_or_blood_group=configuration.require_new_donor_having_better_match_in_compatibility_index_or_blood_group,
            use_binary_scoring=configuration.use_binary_scoring)

        return hla_additive_scorer

    @staticmethod
    def _blood_group_bonus(donor: Donor, recipient: Recipient):
        if blood_groups_compatible(donor, recipient):
            return BLOOD_GROUP_COMPATIBILITY_BONUS
        else:
            return 0.0
