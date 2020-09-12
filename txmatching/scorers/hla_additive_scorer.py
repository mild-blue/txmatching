from typing import Optional

from txmatching.config.configuration import (Configuration)
from txmatching.config.subclasses import ForbiddenCountryCombination
from txmatching.patients.patient import Donor, Recipient
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.scorer_constants import TRANSPLANT_IMPOSSIBLE_SCORE
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.hla_system.compatibility_index import \
    compatibility_index
from txmatching.utils.hla_system.hla_table import broad_to_split, is_split


class HLAAdditiveScorer(AdditiveScorer):
    def __init__(self, configuration: Configuration = Configuration()):
        super().__init__(configuration.manual_donor_recipient_scores)
        self._configuration = configuration

    # pylint: disable=too-many-return-statements
    # it seems that it is reasonable to want many return statements here as it is still well readable
    def score_transplant_calculated(self, donor: Donor, recipient: Recipient) -> float:
        donor_recipient_ci = compatibility_index(donor.parameters, recipient.parameters)
        related_donor_recipient_ci = compatibility_index(recipient.related_donor.parameters, recipient.parameters)

        # We can't do exchanges between some countries

        if ForbiddenCountryCombination(donor.parameters.country_code, recipient.parameters.country_code) \
                in self._configuration.forbidden_country_combinations:
            return TRANSPLANT_IMPOSSIBLE_SCORE

        # Donor must have blood group that is acceptable for recipient
        if donor.parameters.blood_group not in recipient.acceptable_blood_groups:
            return TRANSPLANT_IMPOSSIBLE_SCORE

        # Recipient can't have antibodies that donor has antigens for
        # TODO: https://trello.com/c/ly8SDkhZ Use allow_low_high_res_incompatible param here
        #  that if set to True would not return TRANSPLANT_IMPOSSIBLE in some cases
        is_positive_hla_crossmatch = self._is_positive_hla_crossmatch(donor, recipient)
        if is_positive_hla_crossmatch is True or is_positive_hla_crossmatch is None:
            return TRANSPLANT_IMPOSSIBLE_SCORE

        # If required, donor must have either better match in blood group or better compatibility index than
        # the donor related to the recipient
        if self._configuration.require_new_donor_having_better_match_in_compatibility_index_or_blood_group \
                and (not blood_groups_compatible(donor, recipient)
                     and donor_recipient_ci <= related_donor_recipient_ci):
            return TRANSPLANT_IMPOSSIBLE_SCORE

        # If required, the donor must have the compatible blood group with recipient
        if self._configuration.enforce_compatible_blood_group and not blood_groups_compatible(donor, recipient):
            return TRANSPLANT_IMPOSSIBLE_SCORE

        # If required, the compatibility index between donor and recipient must be higher than
        # between recipient and the donor related to him
        if self._configuration.require_new_donor_having_better_match_in_compatibility_index \
                and donor_recipient_ci <= related_donor_recipient_ci:
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

    # pylint: enable=too-many-return-statements

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'HLAAdditiveScorer':
        hla_additive_scorer = HLAAdditiveScorer(configuration)
        return hla_additive_scorer

    def _blood_group_compatibility_bonus(self, donor: Donor, recipient: Recipient):
        if blood_groups_compatible(donor, recipient):
            return self._configuration.blood_group_compatibility_bonus
        else:
            return 0.0

    @staticmethod
    def _is_positive_hla_crossmatch(donor: Donor, recipient: Recipient) -> Optional[bool]:
        """
        Do donor and recipient have positive crossmatch in HLA system?
        If this can't be determined, return None
        e.g. A23 -> A23 True
             A9 -> A9  True -- A9 in antibodies indicates wider range of antibodies, in this case A23, A24
             A23 -> A9 True
             A23 -> A24 False
             A9 -> A23 None -- A9 in antigens indicates incomplete information
        :param donor:
        :param recipient:
        :return:
        """
        positive_crossmatch = True
        negative_crossmatch = False
        crossmatch_cant_be_determined = None

        recipient_antibodies = recipient.parameters.hla_antibodies.codes
        recipient_antibodies_with_splits = list(recipient_antibodies)

        for antibody_code in recipient_antibodies:
            split_codes = broad_to_split.get(antibody_code)
            if split_codes is not None:
                recipient_antibodies_with_splits.extend(split_codes)

        crossmatch_cant_be_determined_so_far = False

        for antigen_code in donor.parameters.hla_antigens.codes:
            code_is_split = is_split(antigen_code)

            if code_is_split is True or code_is_split is None:  # Code is split or we don't know
                if antigen_code in recipient_antibodies_with_splits:
                    return positive_crossmatch
            else:  # Code is broad
                if antigen_code in recipient_antibodies:
                    return positive_crossmatch

                antigen_splits = broad_to_split.get(antigen_code)
                if antigen_splits is not None:
                    for antigen_split in antigen_splits:
                        if antigen_split in recipient_antibodies:
                            crossmatch_cant_be_determined_so_far = True

        if crossmatch_cant_be_determined_so_far is True:
            return crossmatch_cant_be_determined

        return negative_crossmatch
