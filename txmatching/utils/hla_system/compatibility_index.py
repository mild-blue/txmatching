import logging
from dataclasses import dataclass
from typing import List

from txmatching.patients.hla_model import HLAType, HLATyping
from txmatching.utils.enums import (HLA_GROUPS_GENE,
                                    HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS,
                                    MATCH_TYPE_BONUS, HLAGroup, MatchTypes)
# Traditionally one can calculate index of incompatibility (IK) - the higher IK the higher incompatibility.
# You calculate it by calculating the number of differences in A, B, DR alleles and look up the corresponding
# column in the incompatibility index table.
# For our purposes, we will use the index of compatibility, which is the inverse of index of incompatibility
# -- see function compatibility_index -- and is calculated as the number of matches in A, B, DR alleles.
# For each matching allele a certain bonus is added to compatibility index depending on the allele type.
from txmatching.utils.hla_system.hla_transformations import (broad_to_split,
                                                             get_broad_codes)

logger = logging.getLogger(__name__)


class InvalidNumberOfAllelesError(Exception):
    pass


@dataclass(unsafe_hash=True)
class HLAMatch:
    hla_type: HLAType
    match_type: MatchTypes


@dataclass
class DetailedCompatibilityIndexForHLAGroup:
    hla_group: HLAGroup
    donor_matches: List[HLAMatch]
    recipient_matches: List[HLAMatch]
    group_compatibility_index: float


def compatibility_index(donor_hla_typing: HLATyping,
                        recipient_hla_typing: HLATyping) -> float:
    return sum([ci_index_for_group.group_compatibility_index for ci_index_for_group
                in get_detailed_compatibility_index(donor_hla_typing, recipient_hla_typing)
                ])


def get_detailed_compatibility_index(donor_hla_typing: HLATyping,
                                     recipient_hla_typing: HLATyping
                                     ) -> List[DetailedCompatibilityIndexForHLAGroup]:
    """
    The "compatibility index" is terminus technicus defined by immunologist:
    we calculate number of matches per Compatibility HLA indices and add bonus according
     to number of matches and the HLA code.
    This function thus should not be modified unless after consulting with immunologists.
    """
    hla_compatibility_index_detailed = []
    for hla_group in HLA_GROUPS_GENE:
        donor_hla_types = _hla_types_for_gene_hla_group(donor_hla_typing, hla_group)
        recipient_hla_types = _hla_types_for_gene_hla_group(recipient_hla_typing, hla_group)

        hla_compatibility_index_detailed.append(_get_ci_for_recipient_donor_split_codes(
            donor_hla_types=donor_hla_types,
            recipient_hla_types=recipient_hla_types,
            hla_group=hla_group
        )
        )
    hla_group = HLAGroup.Other
    donor_hla_types = _hla_types_for_hla_group(donor_hla_typing, hla_group)
    recipient_hla_types = _hla_types_for_hla_group(recipient_hla_typing, hla_group)
    hla_compatibility_index_detailed.append(_get_ci_for_recipient_donor_split_codes(
        donor_hla_types=donor_hla_types,
        recipient_hla_types=recipient_hla_types,
        hla_group=hla_group
    ))

    return hla_compatibility_index_detailed


def get_detailed_compatibility_index_without_recipient(donor_hla_typing: HLATyping,
                                                       ) -> List[DetailedCompatibilityIndexForHLAGroup]:
    hla_compatibility_index_detailed = []
    for hla_group in HLA_GROUPS_GENE:  # why not HLA_GROUPS_GENE + [HLAGroup.Other]?
        donor_hla_types = _hla_types_for_gene_hla_group(donor_hla_typing, hla_group)
        donor_matches = [HLAMatch(donor_hla, MatchTypes.NONE) for donor_hla in donor_hla_types]
        hla_compatibility_index_detailed.append(
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=hla_group,
                donor_matches=donor_matches,
                recipient_matches=[],
                group_compatibility_index=0
            )
        )

    hla_group = HLAGroup.Other
    donor_hla_types = _hla_types_for_hla_group(donor_hla_typing, hla_group)
    donor_matches = [HLAMatch(donor_hla, MatchTypes.NONE) for donor_hla in donor_hla_types]
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
def _match_through_split_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               donor_split_codes: List[HLAType],
                               recipient_split_codes: List[HLAType],
                               hla_group: HLAGroup):
    for split_code in donor_split_codes.copy():
        if split_code in recipient_split_codes:
            donor_split_codes.remove(split_code)
            recipient_split_codes.remove(split_code)

            donor_matches.append(HLAMatch(split_code, MatchTypes.SPLIT))
            recipient_matches.append(HLAMatch(split_code, MatchTypes.SPLIT))
            current_compatibility_index += MATCH_TYPE_BONUS[MatchTypes.SPLIT] * HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS[
                hla_group]
    return current_compatibility_index


def _hla_type_to_broad(hla_types: List[HLAType]) -> List[str]:
    return get_broad_codes(
        [hla_type.code for hla_type in hla_types]
    )


def _match_through_broad_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               donor_hla_types: List[HLAType],
                               recipient_hla_types: List[HLAType],
                               hla_group: HLAGroup):
    for hla_type, broad_code in zip(donor_hla_types.copy(), _hla_type_to_broad(donor_hla_types)):
        if broad_code in _hla_type_to_broad(recipient_hla_types):
            matching_hla_types = [recipient_hla_type for recipient_hla_type in recipient_hla_types if
                                  recipient_hla_type.code == broad_code]
            if len(matching_hla_types) > 0:
                recipient_match_hla_type = matching_hla_types[0]
            else:
                split_codes_for_broad = broad_to_split(broad_code)
                hla_types_to_remove = {recipient_hla_type for recipient_hla_type in recipient_hla_types if
                                       recipient_hla_type.code in split_codes_for_broad}
                assert len(hla_types_to_remove) > 0
                recipient_match_hla_type = hla_types_to_remove.pop()

            recipient_hla_types.remove(recipient_match_hla_type)
            donor_hla_types.remove(hla_type)
            donor_matches.append(HLAMatch(hla_type, MatchTypes.BROAD))
            recipient_matches.append(HLAMatch(recipient_match_hla_type, MatchTypes.BROAD))
            current_compatibility_index += MATCH_TYPE_BONUS[MatchTypes.BROAD] * HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS[
                hla_group]
    return current_compatibility_index


# pylint: enable=too-many-arguments


def _get_ci_for_recipient_donor_split_codes(
        donor_hla_types: List[HLAType],
        recipient_hla_types: List[HLAType],
        hla_group: HLAGroup) -> DetailedCompatibilityIndexForHLAGroup:
    donor_matches = []
    recipient_matches = []

    group_compatibility_index = _match_through_split_codes(0.0,
                                                           donor_matches,
                                                           recipient_matches,
                                                           donor_hla_types,
                                                           recipient_hla_types,
                                                           hla_group)
    group_compatibility_index = _match_through_broad_codes(group_compatibility_index,
                                                           donor_matches,
                                                           recipient_matches,
                                                           donor_hla_types,
                                                           recipient_hla_types,
                                                           hla_group)

    for left_recipient_hla_type in recipient_hla_types:
        recipient_matches.append(HLAMatch(left_recipient_hla_type, MatchTypes.NONE))
    for left_donor_hla_type in donor_hla_types:
        donor_matches.append(HLAMatch(left_donor_hla_type, MatchTypes.NONE))

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
