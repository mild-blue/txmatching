import logging
from dataclasses import dataclass
from typing import Callable, Dict, List

from txmatching.patients.hla_model import HLAType, HLATyping
from txmatching.utils.enums import (GENE_HLA_GROUPS,
                                    GENE_HLA_GROUPS_WITH_OTHER, HLAGroup,
                                    MatchType)

# Traditionally one can calculate index of incompatibility (IK) - the higher IK the higher incompatibility.
# You calculate it by calculating the number of differences in A, B, DR alleles and look up the corresponding
# column in the incompatibility index table.
# For our purposes, we will use the index of compatibility, which is the inverse of index of incompatibility
# -- see function compatibility_index -- and is calculated as the number of matches in A, B, DR alleles.
# For each matching allele a certain bonus is added to compatibility index depending on the allele type.

logger = logging.getLogger(__name__)


class InvalidNumberOfAllelesError(Exception):
    pass


@dataclass(unsafe_hash=True)
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
    def hla_typing_bonus_per_groups(self) -> Dict[HLAGroup, int]:
        raise NotImplementedError('Has to be overridden')

    def compute_match_compatibility_index(self, match_type: MatchType, hla_group: HLAGroup):
        return self.match_type_bonus[match_type] * self.hla_typing_bonus_per_groups[hla_group]


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
    def hla_typing_bonus_per_groups(self):
        return {
            HLAGroup.A: 0,
            HLAGroup.B: 0,
            HLAGroup.DRB1: 0,
            HLAGroup.Other: 0
        }


def compatibility_index(donor_hla_typing: HLATyping,
                        recipient_hla_typing: HLATyping,
                        ci_configuration: CIConfiguration = None) -> float:
    if ci_configuration is None:
        ci_configuration = DefaultCIConfiguration()

    return sum([ci_index_for_group.group_compatibility_index for ci_index_for_group
                in get_detailed_compatibility_index(donor_hla_typing, recipient_hla_typing, ci_configuration)
                ])


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
    for hla_group in GENE_HLA_GROUPS_WITH_OTHER:
        if hla_group in GENE_HLA_GROUPS:
            donor_hla_types = _hla_types_for_gene_hla_group(donor_hla_typing, hla_group)
            recipient_hla_types = _hla_types_for_gene_hla_group(recipient_hla_typing, hla_group)
        else:
            donor_hla_types = _hla_types_for_hla_group(donor_hla_typing, hla_group)
            recipient_hla_types = _hla_types_for_hla_group(recipient_hla_typing, hla_group)

        hla_compatibility_index_detailed.append(_get_ci_for_recipient_donor_split_codes(
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
    for hla_group in GENE_HLA_GROUPS_WITH_OTHER:
        donor_hla_types = _hla_types_for_gene_hla_group(donor_hla_typing, hla_group)
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
                          donor_hla_types: List[HLAType],
                          recipient_hla_types: List[HLAType],
                          hla_group: HLAGroup,
                          matching_hla_types_func: Callable[[HLAType, HLAType], bool],
                          result_match_type: MatchType,
                          ci_configuration: CIConfiguration):
    for donor_hla_type in donor_hla_types.copy():
        matching_hla_types = [recipient_hla_type for recipient_hla_type in recipient_hla_types if
                              matching_hla_types_func(recipient_hla_type, donor_hla_type)]
        if len(matching_hla_types) > 0:
            donor_hla_types.remove(donor_hla_type)
            recipient_hla_types.remove(matching_hla_types[0])

            donor_matches.append(HLAMatch(donor_hla_type, result_match_type))
            recipient_matches.append(HLAMatch(matching_hla_types[0], result_match_type))
            current_compatibility_index += ci_configuration.compute_match_compatibility_index(
                result_match_type, hla_group
            )
    return current_compatibility_index


def _match_through_high_res_codes(current_compatibility_index: float,
                                  donor_matches: List[HLAMatch],
                                  recipient_matches: List[HLAMatch],
                                  donor_hla_types: List[HLAType],
                                  recipient_hla_types: List[HLAType],
                                  hla_group: HLAGroup,
                                  ci_configuration: CIConfiguration):
    return _match_through_lambda(
        current_compatibility_index,
        donor_matches,
        recipient_matches,
        donor_hla_types,
        recipient_hla_types,
        hla_group,
        lambda recipient_hla_type, donor_hla_type:
        recipient_hla_type.code.high_res == donor_hla_type.code.high_res and donor_hla_type.code.high_res is not None,
        MatchType.HIGH_RES,
        ci_configuration
    )


def _match_through_split_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               donor_hla_types: List[HLAType],
                               recipient_hla_types: List[HLAType],
                               hla_group: HLAGroup,
                               ci_configuration: CIConfiguration):
    return _match_through_lambda(
        current_compatibility_index,
        donor_matches,
        recipient_matches,
        donor_hla_types,
        recipient_hla_types,
        hla_group,
        lambda recipient_hla_type, donor_hla_type:
        recipient_hla_type.code.split == donor_hla_type.code.split and donor_hla_type.code.split is not None,
        MatchType.SPLIT,
        ci_configuration
    )


def _match_through_broad_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               donor_hla_types: List[HLAType],
                               recipient_hla_types: List[HLAType],
                               hla_group: HLAGroup,
                               ci_configuration: CIConfiguration):
    return _match_through_lambda(
        current_compatibility_index,
        donor_matches,
        recipient_matches,
        donor_hla_types,
        recipient_hla_types,
        hla_group,
        lambda recipient_hla_type, donor_hla_type:
        recipient_hla_type.code.broad == donor_hla_type.code.broad,
        MatchType.BROAD,
        ci_configuration
    )


# pylint: enable=too-many-arguments


def _get_ci_for_recipient_donor_split_codes(
        donor_hla_types: List[HLAType],
        recipient_hla_types: List[HLAType],
        hla_group: HLAGroup,
        ci_configuration: CIConfiguration) -> DetailedCompatibilityIndexForHLAGroup:
    donor_matches = []
    recipient_matches = []

    group_compatibility_index = _match_through_high_res_codes(0.0,
                                                              donor_matches,
                                                              recipient_matches,
                                                              donor_hla_types,
                                                              recipient_hla_types,
                                                              hla_group,
                                                              ci_configuration)
    group_compatibility_index = _match_through_split_codes(group_compatibility_index,
                                                           donor_matches,
                                                           recipient_matches,
                                                           donor_hla_types,
                                                           recipient_hla_types,
                                                           hla_group,
                                                           ci_configuration)
    group_compatibility_index = _match_through_broad_codes(group_compatibility_index,
                                                           donor_matches,
                                                           recipient_matches,
                                                           donor_hla_types,
                                                           recipient_hla_types,
                                                           hla_group,
                                                           ci_configuration)

    for recipient_hla_type in recipient_hla_types:
        recipient_matches.append(HLAMatch(recipient_hla_type, MatchType.NONE))
    for donor_hla_type in donor_hla_types:
        donor_matches.append(HLAMatch(donor_hla_type, MatchType.NONE))

    return DetailedCompatibilityIndexForHLAGroup(
        hla_group=hla_group,
        donor_matches=donor_matches,
        recipient_matches=recipient_matches,
        group_compatibility_index=group_compatibility_index
    )


def _hla_types_for_gene_hla_group(donor_hla_typing: HLATyping, hla_group: HLAGroup) -> List[HLAType]:
    hla_types = _hla_types_for_hla_group(donor_hla_typing, hla_group)

    if len(hla_types) not in {1, 2}:
        logger.error(
            f'Invalid list of alleles for gene {hla_group.name} - there have to be 1 or 2 per gene.'
            f'\nList of patient_alleles: {donor_hla_typing.hla_per_groups}')
        return hla_types
    if len(hla_types) == 1:
        return hla_types + hla_types
    return hla_types


def _hla_types_for_hla_group(donor_hla_typing: HLATyping, hla_group: HLAGroup) -> List[HLAType]:
    return next(hla_per_group.hla_types for hla_per_group in donor_hla_typing.hla_per_groups if
                hla_per_group.hla_group == hla_group).copy()
