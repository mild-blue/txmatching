from abc import ABC
from typing import List, Optional

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.configuration.subclasses import ForbiddenCountryCombination
from txmatching.patients.patient import Donor, Recipient
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.scorer_constants import NEGATIVE_SCORE_BINARY_MODE, POSITIVE_SCORE_BINARY_MODE, \
    TRANSPLANT_IMPOSSIBLE_SCORE
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.enums import HLA_GROUPS_PROPERTIES
from txmatching.utils.hla_system.compatibility_index import (
    CIConfiguration, compatibility_index)
from txmatching.utils.hla_system.hla_crossmatch import \
    is_positive_hla_crossmatch


class HLAAdditiveScorer(AdditiveScorer, ABC):
    def __init__(self, config_parameters: ConfigParameters = ConfigParameters()):
        super().__init__(config_parameters.manual_donor_recipient_scores)
        self._configuration = config_parameters

    @property
    def ci_configuration(self) -> CIConfiguration:
        raise NotImplementedError('Has to be overridden')

    @property
    def max_transplant_score(self) -> float:
        # TODO?
        max_value = max(self.ci_configuration.match_type_bonus.values()) * sum(
            bonus * HLA_GROUPS_PROPERTIES[group].max_count_per_patient for group, bonus in
            self.ci_configuration.hla_typing_bonus_per_groups_without_dp_dq.items()) \
                    + self._configuration.blood_group_compatibility_bonus
        return max_value

    # in order to get the correct score in binary mode with manual score set, we should check few conditions
    def get_score_when_manual_score_set(self, manual_score):
        if self._configuration.use_binary_scoring:
            if manual_score >= 0:
                return POSITIVE_SCORE_BINARY_MODE
            else:
                return NEGATIVE_SCORE_BINARY_MODE
        else:
            return manual_score

    # it seems that it is reasonable to want many return statements here as it is still well readable
    # pylint: disable=too-many-return-statements
    def score_transplant_calculated(self, donor: Donor, recipient: Recipient,
                                    original_donors: Optional[List[Donor]]) -> float:
        donor_recipient_ci = compatibility_index(
            donor.parameters.hla_typing,
            recipient.parameters.hla_typing,
            ci_configuration=self.ci_configuration
        )
        if original_donors:
            all_related_donors_recipient_ci = [
                compatibility_index(original_donor.parameters.hla_typing, recipient.parameters.hla_typing,
                                    ci_configuration=self.ci_configuration) for original_donor in original_donors]
            best_related_donor_recipient_ci = max(all_related_donors_recipient_ci)
        else:
            best_related_donor_recipient_ci = 0.0

        # We can't do exchanges between some countries
        if ForbiddenCountryCombination(donor.parameters.country_code, recipient.parameters.country_code) \
                in self._configuration.forbidden_country_combinations:
            return TRANSPLANT_IMPOSSIBLE_SCORE

        # Donor must have blood group that is acceptable or compatible for the recipient
        if not (donor.parameters.blood_group in recipient.acceptable_blood_groups
                or blood_groups_compatible(donor.parameters.blood_group, recipient.parameters.blood_group)):
            return TRANSPLANT_IMPOSSIBLE_SCORE

        # Recipient can't have antibodies that donor has hla_typing for
        positive_crossmatch = is_positive_hla_crossmatch(donor.parameters.hla_typing,
                                                         recipient.hla_antibodies,
                                                         self._configuration.use_high_resolution,
                                                         self._configuration.hla_crossmatch_level)
        if positive_crossmatch:
            return TRANSPLANT_IMPOSSIBLE_SCORE

        better_match_in_ci_or_br = self._get_setting_from_config_or_recipient(
            recipient,
            'require_better_match_in_compatibility_index_or_blood_group'
        )

        if better_match_in_ci_or_br and (
                not blood_groups_compatible(donor.parameters.blood_group, recipient.parameters.blood_group)
                and donor_recipient_ci <= best_related_donor_recipient_ci):
            return TRANSPLANT_IMPOSSIBLE_SCORE
        require_compatible_blood_group = self._get_setting_from_config_or_recipient(recipient,
                                                                                    'require_compatible_blood_group') or \
                                         self._configuration.require_compatible_blood_group
        # If required, the donor must have the compatible blood group with recipient
        if require_compatible_blood_group and not blood_groups_compatible(donor.parameters.blood_group,
                                                                          recipient.parameters.blood_group):
            return TRANSPLANT_IMPOSSIBLE_SCORE

        better_match_in_ci = self._get_setting_from_config_or_recipient(recipient,
                                                                        'require_better_match_in_compatibility_index')
        # If required, the compatibility index between donor and recipient must be higher than
        # between recipient and the donor related to him
        if better_match_in_ci and donor_recipient_ci <= best_related_donor_recipient_ci:
            return TRANSPLANT_IMPOSSIBLE_SCORE

        if self._configuration.use_binary_scoring:
            return 1.0
        else:
            blood_group_bonus = self._blood_group_compatibility_bonus(donor, recipient)
            total_score = donor_recipient_ci + blood_group_bonus

            # The total score must be higher than the minimum required
            if total_score < self._configuration.minimum_total_score:
                return TRANSPLANT_IMPOSSIBLE_SCORE
            else:
                return total_score

    def _blood_group_compatibility_bonus(self, donor: Donor, recipient: Recipient):
        if blood_groups_compatible(donor.parameters.blood_group, recipient.parameters.blood_group):
            return self._configuration.blood_group_compatibility_bonus
        else:
            return 0.0

    def _get_setting_from_config_or_recipient(self, recipient: Recipient,
                                              setting_name):
        setting_val = getattr(recipient.recipient_requirements, setting_name)
        return setting_val if setting_val is not None else getattr(self._configuration, setting_name)
