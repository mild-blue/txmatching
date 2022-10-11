import functools
from dataclasses import dataclass
from typing import List, Callable, Optional, Set, Tuple

from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody, HLAType, HLATyping, HLAPerGroup
from txmatching.utils.enums import (AntibodyMatchTypes, HLACrossmatchLevel,
                                    HLAGroup)

MINIMUM_REQUIRED_ANTIBODIES_FOR_TYPE_A = 20


@dataclass(eq=True, frozen=True)
class AntibodyMatch:
    hla_antibody: HLAAntibody
    match_type: AntibodyMatchTypes


@dataclass
class AntibodyMatchForHLAGroup:
    hla_group: HLAGroup
    antibody_matches: List[AntibodyMatch]


def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_high_resolution: bool,
                                soft_cutoff: int) -> Tuple[List[AntibodyMatchForHLAGroup],
                                                           List[AntibodyMatchForHLAGroup]]:
    if use_high_resolution and is_recipient_type_a(recipient_antibodies):
        crossmatch_function = get_crossmatched_antibodies__type_a
    else:
        crossmatch_function = get_crossmatched_antibodies__type_b

    antibody_matches_for_groups = crossmatch_function(donor_hla_typing,
                                                      recipient_antibodies,
                                                      soft_cutoff=None)

    antibody_soft_matches_for_groups = crossmatch_function(donor_hla_typing,
                                                           recipient_antibodies,
                                                           soft_cutoff)

    # Sort antibodies
    for antibodies_per_hla_group in antibody_matches_for_groups:
        antibodies_per_hla_group.antibody_matches.sort(key=lambda hla_group: hla_group.hla_antibody.raw_code)

    # Sort antibodies with soft crossmatch
    for antibodies_per_hla_group in antibody_soft_matches_for_groups:
        antibodies_per_hla_group.antibody_matches.sort(key=lambda hla_group: hla_group.hla_antibody.raw_code)

    return antibody_matches_for_groups, antibody_soft_matches_for_groups


def is_positive_hla_crossmatch(donor_hla_typing: HLATyping,
                               recipient_antibodies: HLAAntibodies,
                               use_high_resolution: Optional[bool],
                               crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE,
                               crossmatch_logic: Callable = get_crossmatched_antibodies,
                               soft_cutoff: Optional[int] = None) -> bool:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    e.g. A23 -> A23 True
         A9 -> A9  True
         A23 -> A9 True
         A23 -> A24 False if use_high_resolution else True
         A9 -> A23 True
         A9 broad <=> A23, A24 split
    :param donor_hla_typing: donor hla_typing to crossmatch
    :param recipient_antibodies: recipient antibodies to crossmatch
    :param use_high_resolution: setting whether to high res resolution for crossmatch determination
    :param crossmatch_level:
    :param crossmatch_logic:
    :param soft_cutoff:
    :return:
    """

    if crossmatch_logic == get_crossmatched_antibodies:
        crossmatched_antibodies = \
            crossmatch_logic(donor_hla_typing, recipient_antibodies, use_high_resolution, soft_cutoff)[0]
    else:
        crossmatched_antibodies = \
            crossmatch_logic(donor_hla_typing, recipient_antibodies, soft_cutoff)

    common_codes = {antibody_match.hla_antibody for antibody_match_group in
                    crossmatched_antibodies
                    for antibody_match in antibody_match_group.antibody_matches
                    if antibody_match.match_type.is_positive_for_level(crossmatch_level)}
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


# pylint: disable=too-many-branches
def get_crossmatched_antibodies__type_a(donor_hla_typing: HLATyping,
                                        recipient_antibodies: HLAAntibodies,
                                        soft_cutoff: Optional[int] = None) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        positive_matches = set()
        antibodies = antibodies_per_group.hla_antibody_list

        for hla_type in hla_per_group.hla_types:
            if hla_type.code.high_res is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.high_res == antibody.code.high_res]

                # HIGH_RES_1
                if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.HIGH_RES, positive_matches, soft_cutoff):
                    continue

                if not _recipient_was_tested_for_donor_antigen(antibodies, hla_type.code):
                    tested_antibodies_that_match = [antibody for antibody in antibodies
                                                    if hla_type.code.split == antibody.code.split
                                                    if hla_type.code.split is not None]
                    positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                    # HIGH_RES_2
                    if soft_cutoff is None:
                        if _add_all_tested_positive_antibodies(tested_antibodies_that_match,
                                                               positive_tested_antibodies,
                                                               AntibodyMatchTypes.HIGH_RES,
                                                               positive_matches):
                            continue

                    # HIGH_RES_WITH_SPLIT_2
                    if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT, positive_matches, soft_cutoff):
                        continue

            if (hla_type.code.split is not None
                    # TODO: Is necessary this condition?
                    and hla_type.code.high_res is None):
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split
                                                if hla_type.code.split is not None]
                positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                # HIGH_RES_3
                if soft_cutoff is None:
                    if _add_all_tested_positive_antibodies(tested_antibodies_that_match,
                                                           positive_tested_antibodies,
                                                           AntibodyMatchTypes.HIGH_RES,
                                                           positive_matches):
                        continue

                # HIGH_RES_WITH_SPLIT_1
                if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT, positive_matches, soft_cutoff):
                    continue

                # SPLIT_1
                if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.SPLIT, positive_matches, soft_cutoff):
                    continue

            if (hla_type.code.broad is not None
                    # TODO: Is necessary this condition?
                    and (hla_type.code.high_res is None and hla_type.code.split is None)):
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.broad == antibody.code.broad]
                positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                # HIGH_RES_3
                if soft_cutoff is None:
                    if _add_all_tested_positive_antibodies(tested_antibodies_that_match,
                                                           positive_tested_antibodies,
                                                           AntibodyMatchTypes.HIGH_RES,
                                                           positive_matches):
                        continue

                # HIGH_RES_WITH_BROAD_1
                if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.HIGH_RES_WITH_BROAD, positive_matches, soft_cutoff):
                    continue

                # BROAD_1
                if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.BROAD, positive_matches, soft_cutoff):
                    continue

        _add_undecidable_typization(antibodies, hla_per_group, positive_matches, soft_cutoff)

        if soft_cutoff is None:
            _add_none_typization(antibodies, positive_matches)

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, list(positive_matches)))

    return antibody_matches_for_groups


def get_crossmatched_antibodies__type_b(donor_hla_typing: HLATyping,
                                        recipient_antibodies: HLAAntibodies,
                                        soft_cutoff: Optional[int] = None) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        positive_matches = set()
        antibodies = antibodies_per_group.hla_antibody_list

        for hla_type in hla_per_group.hla_types:
            if hla_type.code.high_res is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.high_res == antibody.code.high_res]
                # HIGH_RES_1
                if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.HIGH_RES, positive_matches, soft_cutoff):
                    continue

            if hla_type.code.split is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split
                                                if hla_type.code.split is not None]
                if _add_split_typization(hla_type, tested_antibodies_that_match, positive_matches, soft_cutoff):
                    continue

            if hla_type.code.broad is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.broad == antibody.code.broad]
                if _add_broad_typization(hla_type, tested_antibodies_that_match, positive_matches, soft_cutoff):
                    continue

        _add_undecidable_typization(antibodies, hla_per_group, positive_matches, soft_cutoff)

        if soft_cutoff is None:
            _add_none_typization(antibodies, positive_matches)

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, list(positive_matches)))

    return antibody_matches_for_groups


def is_recipient_type_a(recipient_antibodies: HLAAntibodies) -> bool:
    total_antibodies = 0
    is_at_least_one_antibody_below_cutoff = False

    # TODO: https://github.com/mild-blue/txmatching/issues/1012
    #  Better looping
    for antibodies_per_group in recipient_antibodies.hla_antibodies_per_groups:
        total_antibodies += len(antibodies_per_group.hla_antibody_list)
        for hla_antibody in antibodies_per_group.hla_antibody_list:
            if hla_antibody.code.high_res is None:
                return False
            if hla_antibody.mfi < hla_antibody.cutoff:
                is_at_least_one_antibody_below_cutoff = True

    if total_antibodies < MINIMUM_REQUIRED_ANTIBODIES_FOR_TYPE_A:
        return False

    if not is_at_least_one_antibody_below_cutoff:
        return False

    return True


def _get_antibodies_over_cutoff(antibodies: List[HLAAntibody]) -> List[HLAAntibody]:
    return [antibody for antibody in antibodies if antibody.mfi >= antibody.cutoff]


def _get_antibodies_fulfilling_soft_crossmatch(soft_cutoff: int, antibodies: List[HLAAntibody]) -> List[HLAAntibody]:
    return [antibody for antibody in antibodies if soft_cutoff <= antibody.mfi <= antibody.cutoff]


def _recipient_was_tested_for_donor_antigen(antibodies: List[HLAAntibody], antigen: HLACode) -> bool:
    return antigen in [antibody.code for antibody in antibodies]


def _add_all_tested_positive_antibodies(tested_antibodies_that_match: List[HLAAntibody],
                                        positive_tested_antibodies: List[HLAAntibody],
                                        match_type: AntibodyMatchTypes,
                                        positive_matches: Set[AntibodyMatch]) -> bool:
    if len(positive_tested_antibodies) > 0:
        if len(tested_antibodies_that_match) == len(positive_tested_antibodies):
            for antibody in tested_antibodies_that_match:
                positive_matches.add(AntibodyMatch(antibody, match_type))
            return len(tested_antibodies_that_match) > 0
    return False


def _add_tested_antibodies(tested_antibodies_that_match: List[HLAAntibody],
                           match_type: AntibodyMatchTypes,
                           positive_matches: Set[AntibodyMatch],
                           soft_cutoff: Optional[int]) -> bool:
    if soft_cutoff is None:
        filter_function = _get_antibodies_over_cutoff
    else:
        filter_function = functools.partial(_get_antibodies_fulfilling_soft_crossmatch, soft_cutoff)

    if len(tested_antibodies_that_match) > 0:
        filtered_antibodies = filter_function(tested_antibodies_that_match)
        for antibody in filtered_antibodies:
            positive_matches.add(AntibodyMatch(antibody, match_type))
        return len(filtered_antibodies) > 0
    return False


def _add_split_typization(hla_type: HLAType,
                          tested_antibodies_that_match: List[HLAAntibody],
                          positive_matches: Set[AntibodyMatch],
                          soft_cutoff: int) -> bool:
    """Return True if split crossmatching has happened."""

    # SPLIT_1
    if hla_type.code.high_res is None:
        if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.SPLIT, positive_matches, soft_cutoff):
            return True

    tested_antibodies_that_match = [antibody for antibody in tested_antibodies_that_match
                                    if antibody.code.high_res is None]
    # SPLIT_2
    if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.SPLIT, positive_matches, soft_cutoff):
        return True

    return False


def _add_broad_typization(hla_type: HLAType,
                          tested_antibodies_that_match: List[HLAAntibody],
                          positive_matches: Set[AntibodyMatch],
                          soft_cutoff: int) -> bool:
    """Return True if broad crossmatching has happened."""

    # BROAD_1
    if hla_type.code.high_res is None and hla_type.code.split is None:
        if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.BROAD, positive_matches, soft_cutoff):
            return True

    tested_antibodies_that_match = [antibody for antibody in tested_antibodies_that_match
                                    if antibody.code.high_res is None and antibody.code.split is None]
    # BROAD_2
    if _add_tested_antibodies(tested_antibodies_that_match, AntibodyMatchTypes.BROAD, positive_matches, soft_cutoff):
        return True

    return False


def _add_undecidable_typization(antibodies: List[HLAAntibody],
                                hla_per_group: HLAPerGroup,
                                positive_matches: Set[AntibodyMatch],
                                soft_cutoff: Optional[int] = None):
    filter_function = _get_antibodies_over_cutoff \
        if soft_cutoff is None \
        else functools.partial(_get_antibodies_fulfilling_soft_crossmatch, soft_cutoff)

    if hla_per_group.hla_group == HLAGroup.Other:
        groups_other = {hla_type.code.group for hla_type in hla_per_group.hla_types}
        for antibody in filter_function(antibodies):
            if antibody.code.group not in groups_other:
                positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE))


def _add_none_typization(antibodies: List[HLAAntibody],
                         positive_matches: Set[AntibodyMatch]):
    antibodies_positive_matches = {match.hla_antibody for match in positive_matches}
    for antibody in _get_antibodies_over_cutoff(antibodies):
        if antibody not in antibodies_positive_matches:
            positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))
