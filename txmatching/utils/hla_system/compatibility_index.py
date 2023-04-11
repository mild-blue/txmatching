import logging
import re
from dataclasses import dataclass
from typing import Callable, Dict, List

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.patients.hla_model import HLAType, HLATyping
from txmatching.utils.enums import HLA_GROUPS, DQDPChain, HLAGroup, MatchType

# Traditionally one can calculate index of incompatibility (IK) - the higher IK the higher incompatibility.
# You calculate it by calculating the number of differences in A, B, DR alleles and look up the corresponding
# column in the incompatibility index table.
# For our purposes, we will use the index of compatibility, which is the inverse of index of incompatibility
# -- see function compatibility_index -- and is calculated as the number of matches in A, B, DR alleles.
# For each matching allele a certain bonus is added to compatibility index depending on the allele type.

logger = logging.getLogger(__name__)


class InvalidNumberOfAllelesError(Exception):
    pass


@dataclass(frozen=True)
class HLAMatch:
    hla_type: HLAType
    match_type: MatchType


@dataclass
class DetailedCompatibilityIndexForHLAGroup:
    hla_group: HLAGroup
    donor_matches: List[HLAMatch]
    recipient_matches: List[HLAMatch]
    group_compatibility_index: float


# pylint: disable=too-few-public-methods
class CIConfiguration:
    @property
    def match_type_bonus(self) -> Dict[MatchType, int]:
        raise NotImplementedError('Has to be overridden')

    @property
    def hla_typing_bonus_per_groups_without_dp_dq(self) -> Dict[HLAGroup, int]:
        raise NotImplementedError('Has to be overridden')

    @property
    def hla_typing_bonus_per_dp_dq_chains(self) -> Dict[str, int]:
        raise NotImplementedError('Has to be overridden')

    def compute_match_compatibility_index(self, match_type: MatchType, hla_group: HLAGroup) -> float:
        return self.match_type_bonus[match_type] * self.hla_typing_bonus_per_groups_without_dp_dq[hla_group]

    def compute_match_compatibility_index_dp_dq(self, match_type: MatchType, dqdp_allele: DQDPChain) -> float:
        return self.match_type_bonus[match_type] * self.hla_typing_bonus_per_dp_dq_chains[dqdp_allele]


class DefaultCIConfiguration(CIConfiguration):
    @property
    def match_type_bonus(self):
        return {
            MatchType.BROAD: 0,
            MatchType.SPLIT: 0,
            MatchType.HIGH_RES: 0,
            MatchType.NONE: 0,
        }

    @property
    def hla_typing_bonus_per_groups_without_dp_dq(self):
        return {
            HLAGroup.A: 0,
            HLAGroup.B: 0,
            HLAGroup.DRB1: 0,
            HLAGroup.CW: 0,
            HLAGroup.OTHER_DR: 0
        }

    @property
    def hla_typing_bonus_per_dp_dq_chains(self):
        return {
            DQDPChain.ALPHA_DP: 0,
            DQDPChain.ALPHA_DQ: 0,
            DQDPChain.BETA_DP: 0,
            DQDPChain.BETA_DQ: 0,
        }


def compatibility_index(donor_hla_typing: HLATyping,
                        recipient_hla_typing: HLATyping,
                        ci_configuration: CIConfiguration = None) -> float:
    if ci_configuration is None:
        ci_configuration = DefaultCIConfiguration()

    return sum(ci_index_for_group.group_compatibility_index for ci_index_for_group
               in get_detailed_compatibility_index(donor_hla_typing, recipient_hla_typing, ci_configuration))


def get_detailed_compatibility_index(donor_hla_typing: HLATyping,
                                     recipient_hla_typing: HLATyping,
                                     ci_configuration: CIConfiguration = None
                                     ) -> List[DetailedCompatibilityIndexForHLAGroup]:
    """
    The "compatibility index" is terminus technicus defined by immunologist:
    we calculate number of matches per Compatibility HLA indices and add bonus according
     to number of matches and the HLA code.
    This function thus should not be modified unless after consulting with immunologists.
    """
    if ci_configuration is None:
        ci_configuration = DefaultCIConfiguration()

    hla_compatibility_index_detailed = []
    for hla_group in HLA_GROUPS + [HLAGroup.INVALID_CODES]:
        donor_hla_types = _check_if_correct_amount_of_hla_types(donor_hla_typing, hla_group)
        recipient_hla_types = _check_if_correct_amount_of_hla_types(recipient_hla_typing, hla_group)

        hla_compatibility_index_detailed.append(_get_ci_for_recipient_donor_types_in_group(
            donor_hla_types=donor_hla_types,
            recipient_hla_types=recipient_hla_types,
            hla_group=hla_group,
            ci_configuration=ci_configuration
        )
        )

    return hla_compatibility_index_detailed


def get_detailed_compatibility_index_without_recipient(donor_hla_typing: HLATyping,
                                                       ) -> List[DetailedCompatibilityIndexForHLAGroup]:
    hla_compatibility_index_detailed = []
    for hla_group in HLA_GROUPS:
        donor_hla_types = _check_if_correct_amount_of_hla_types(donor_hla_typing, hla_group)
        donor_matches = [HLAMatch(donor_hla, MatchType.NONE) for donor_hla in donor_hla_types]
        hla_compatibility_index_detailed.append(
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=hla_group,
                donor_matches=donor_matches,
                recipient_matches=[],
                group_compatibility_index=0
            )
        )

    return hla_compatibility_index_detailed


# pylint: disable=too-many-arguments
# I think it is reasonable to have multiple arguments here
def _match_through_lambda(current_compatibility_index: float,
                          donor_matches: List[HLAMatch],
                          recipient_matches: List[HLAMatch],
                          remaining_donor_hla_types: List[HLAType],
                          remaining_recipient_hla_types: List[HLAType],
                          hla_group: HLAGroup,
                          matching_hla_types_func: Callable[[HLAType, HLAType], bool],
                          result_match_type: MatchType,
                          ci_configuration: CIConfiguration,
                          recipient_hla_types: List[HLAType]):
    for donor_hla_type in remaining_donor_hla_types.copy():
        matching_hla_types = [recipient_hla_type for recipient_hla_type in recipient_hla_types if
                              matching_hla_types_func(recipient_hla_type, donor_hla_type)]
        if len(matching_hla_types) > 0:
            remaining_donor_hla_types.remove(donor_hla_type)
            recipient_match = HLAMatch(matching_hla_types[0], result_match_type)
            if recipient_match not in recipient_matches and matching_hla_types[0] in remaining_recipient_hla_types:
                remaining_recipient_hla_types.remove(matching_hla_types[0])
                recipient_matches.append(recipient_match)
            donor_matches.append(HLAMatch(donor_hla_type, result_match_type))
            # TODO: change this in the future, this is not the prettiest. this was the easiest way how to add
            # compatibility index for particular DP and DQ subgroups.
            if hla_group in {HLAGroup.DP, HLAGroup.DQ}:
                dq_dp_chain = _which_dq_dp_chain(donor_hla_type)
                current_compatibility_index += ci_configuration.compute_match_compatibility_index_dp_dq(
                    result_match_type, dq_dp_chain
                )
            else:
                current_compatibility_index += ci_configuration.compute_match_compatibility_index(
                    result_match_type, hla_group
                )
    return current_compatibility_index


# TODO check better for the fact that a code has letters at the end maybe add as code property to the object
# https://github.com/mild-blue/txmatching/issues/637
def _match_through_high_res_codes(current_compatibility_index: float,
                                  donor_matches: List[HLAMatch],
                                  recipient_matches: List[HLAMatch],
                                  remaining_donor_hla_types: List[HLAType],
                                  remaining_recipient_hla_types: List[HLAType],
                                  hla_group: HLAGroup,
                                  ci_configuration: CIConfiguration,
                                  recipient_hla_types: List[HLAType]):
    return _match_through_lambda(
        current_compatibility_index,
        donor_matches,
        recipient_matches,
        remaining_donor_hla_types,
        remaining_recipient_hla_types,
        hla_group,
        lambda recipient_hla_type, donor_hla_type:
        recipient_hla_type.code.high_res == donor_hla_type.code.high_res and donor_hla_type.code.high_res is not None
        and _high_res_code_without_letter(donor_hla_type),
        MatchType.HIGH_RES,
        ci_configuration,
        recipient_hla_types
    )


def _match_through_split_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               remaining_donor_hla_types: List[HLAType],
                               remaining_recipient_hla_types: List[HLAType],
                               hla_group: HLAGroup,
                               ci_configuration: CIConfiguration,
                               recipient_hla_types: List[HLAType]):
    return _match_through_lambda(
        current_compatibility_index,
        donor_matches,
        recipient_matches,
        remaining_donor_hla_types,
        remaining_recipient_hla_types,
        hla_group,
        lambda recipient_hla_type, donor_hla_type:
        recipient_hla_type.code.split == donor_hla_type.code.split and donor_hla_type.code.split is not None
        and _high_res_code_without_letter(donor_hla_type),
        MatchType.SPLIT,
        ci_configuration,
        recipient_hla_types
    )


def _match_through_broad_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               remaining_donor_hla_types: List[HLAType],
                               remaining_recipient_hla_types: List[HLAType],
                               hla_group: HLAGroup,
                               ci_configuration: CIConfiguration,
                               recipient_hla_types: List[HLAType]):
    return _match_through_lambda(
        current_compatibility_index,
        donor_matches,
        recipient_matches,
        remaining_donor_hla_types,
        remaining_recipient_hla_types,
        hla_group,
        lambda recipient_hla_type, donor_hla_type:
        recipient_hla_type.code.broad == donor_hla_type.code.broad
        and _high_res_code_without_letter(donor_hla_type),
        MatchType.BROAD,
        ci_configuration,
        recipient_hla_types
    )


# pylint: enable=too-many-arguments


def _get_ci_for_recipient_donor_types_in_group(
        donor_hla_types: List[HLAType],
        recipient_hla_types: List[HLAType],
        hla_group: HLAGroup,
        ci_configuration: CIConfiguration) -> DetailedCompatibilityIndexForHLAGroup:
    donor_matches = []
    recipient_matches = []

    remaining_donor_hla_types = donor_hla_types.copy()
    remaining_recipient_hla_types = recipient_hla_types.copy()

    group_compatibility_index = _match_through_high_res_codes(0.0,
                                                              donor_matches,
                                                              recipient_matches,
                                                              remaining_donor_hla_types,
                                                              remaining_recipient_hla_types,
                                                              hla_group,
                                                              ci_configuration,
                                                              recipient_hla_types)
    group_compatibility_index = _match_through_split_codes(group_compatibility_index,
                                                           donor_matches,
                                                           recipient_matches,
                                                           remaining_donor_hla_types,
                                                           remaining_recipient_hla_types,
                                                           hla_group,
                                                           ci_configuration,
                                                           recipient_hla_types)
    group_compatibility_index = _match_through_broad_codes(group_compatibility_index,
                                                           donor_matches,
                                                           recipient_matches,
                                                           remaining_donor_hla_types,
                                                           remaining_recipient_hla_types,
                                                           hla_group,
                                                           ci_configuration,
                                                           recipient_hla_types)

    for recipient_hla_type in remaining_recipient_hla_types:
        recipient_matches.append(HLAMatch(recipient_hla_type, MatchType.NONE))
    for donor_hla_type in remaining_donor_hla_types:
        donor_matches.append(HLAMatch(donor_hla_type, MatchType.NONE))

    return DetailedCompatibilityIndexForHLAGroup(
        hla_group=hla_group,
        donor_matches=sorted(donor_matches, key=lambda donor_match: donor_match.hla_type.code.display_code),
        recipient_matches=sorted(
            recipient_matches, key=lambda recipient_match: recipient_match.hla_type.code.display_code),
        group_compatibility_index=group_compatibility_index
    )


def _check_if_correct_amount_of_hla_types(hla_typing: HLATyping, hla_group: HLAGroup) -> List[HLAType]:
    hla_types = _hla_types_for_hla_group(hla_typing, hla_group)

    if hla_group in {HLAGroup.DP, HLAGroup.DQ}:
        alpha_genes = []
        beta_genes = []
        for code in hla_types:
            dq_dp_chain = _which_dq_dp_chain(code)
            if dq_dp_chain in [DQDPChain.ALPHA_DP, DQDPChain.ALPHA_DQ]:
                alpha_genes.append(code)
            elif dq_dp_chain in [DQDPChain.BETA_DP, DQDPChain.BETA_DQ]:
                beta_genes.append(code)
            else:
                raise InvalidArgumentException(f'Invalid allele for DQ/DP group: {code}')
        if len(alpha_genes) > 2 or len(beta_genes) > 2:
            logger.error(
                f'Invalid list of alleles for group {hla_group.name} - there have to be maximum 2 per gene'
                f'. List of patient alleles in group: {[hla_type.code.display_code for hla_type in hla_types]} '
                f'For the moment this is ignored, in future version it will be an error.')
        if len(alpha_genes) == 1:
            alpha_genes = alpha_genes + alpha_genes
        if len(beta_genes) == 1:
            beta_genes = beta_genes + beta_genes
        return alpha_genes + beta_genes

    if len(hla_types) > 2:
        logger.error(
            f'Invalid list of alleles for gene {hla_group.name} - there have to be maximum 2 per gene.'
            f' List of patient alleles for gene: {[hla_type.code.display_code for hla_type in hla_types]}. '
            f'For the moment this is ignored, in future version it will be an error.')
    if len(hla_types) == 1 and hla_group is not HLAGroup.OTHER_DR:
        return hla_types + hla_types
    return hla_types


def _hla_types_for_hla_group(donor_hla_typing: HLATyping, hla_group: HLAGroup) -> List[HLAType]:
    return next(hla_per_group.hla_types for hla_per_group in donor_hla_typing.hla_per_groups if
                hla_per_group.hla_group == hla_group).copy()


def _high_res_code_without_letter(hla_type: HLAType) -> bool:
    if hla_type.code.high_res is not None:
        return not re.match(r'.*[A-Z]$', hla_type.code.high_res)
    return True


def _which_dq_dp_chain(hla_type: HLAType) -> DQDPChain:
    if hla_type.code.broad:
        code = hla_type.code.broad
    else:
        # For hla code ending with letter, broad code is not specified, check with highres.
        code = hla_type.code.high_res

    if code[:2] == 'DP':
        if code[2] == 'A':
            return DQDPChain.ALPHA_DP
        else:
            return DQDPChain.BETA_DP
    elif code[:2] == 'DQ':
        if code[2] == 'A':
            return DQDPChain.ALPHA_DQ
        else:
            return DQDPChain.BETA_DQ

    raise ValueError(f'HLA type {hla_type.code} does not belong to DP/DQ group')
