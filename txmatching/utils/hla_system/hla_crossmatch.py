from dataclasses import dataclass
from typing import List

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


def is_positive_hla_crossmatch(donor_hla_typing: HLATyping,
                               recipient_antibodies: HLAAntibodies,
                               use_high_resolution: bool,
                               crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE,
                               ) -> bool:
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
    :return:
    """
    common_codes = {antibody_match.hla_antibody for antibody_match_group in
                    get_crossmatched_antibodies(donor_hla_typing, recipient_antibodies, use_high_resolution)
                    for antibody_match in antibody_match_group.antibody_matches
                    if antibody_match.match_type.is_positive_for_level(crossmatch_level)}
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


def _get_antibodies_over_cutoff(antibodies: List[HLAAntibody]) -> List[HLAAntibody]:
    return [antibody for antibody in antibodies if antibody.mfi >= antibody.cutoff]


def _add_undecidable_typization(antibodies: List[HLAAntibody], hla_per_group: HLAPerGroup,
                                positive_matches: List[AntibodyMatch]):
    if hla_per_group.hla_group == HLAGroup.Other:
        groups_other = {hla_type.code.group for hla_type in hla_per_group.hla_types}
        for antibody in antibodies:
            if antibody.code.group not in groups_other:
                positive_matches.append(AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE))


def _add_none_typization(antibodies: List[HLAAntibody],
                         positive_matches: List[AntibodyMatch]):
    antibodies_positive_matches = {match.hla_antibody for match in positive_matches}
    for antibody in _get_antibodies_over_cutoff(antibodies):
        if antibody not in antibodies_positive_matches:
            positive_matches.append(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))


# def _do_crossmatch(tested_antibodies_that_match: List[HLAAntibody], positive_matches: List[AntibodyMatch],
#                    type__all_tested_antibodies_are_positive: AntibodyMatchTypes,
#                    type__only_positive_tested_antibodies: AntibodyMatchTypes) -> bool:
#     """Return `True` if some crossmatching happened."""
#
#     positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)
#
#     if len(positive_tested_antibodies) > 0:
#         if len(tested_antibodies_that_match) == len(positive_tested_antibodies):
#             for match in tested_antibodies_that_match:
#                 positive_matches.append(AntibodyMatch(match, type__all_tested_antibodies_are_positive))
#             return True
#
#         for match in positive_tested_antibodies:
#             positive_matches.append(AntibodyMatch(match, type__only_positive_tested_antibodies))
#         return True
#
#     return len(tested_antibodies_that_match) != 0 or False


def _recipient_was_tested_for_donor_antigen(antibodies: List[HLAAntibody], antigen: HLACode) -> bool:
    return antigen in [antibody.code for antibody in antibodies]


def _do_crossmatch_in_type_a(donor_hla_typing: HLATyping,
                             recipient_antibodies: HLAAntibodies,
                             use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        positive_matches = []
        antibodies = antibodies_per_group.hla_antibody_list

        _add_undecidable_typization(antibodies, hla_per_group, positive_matches)

        for hla_type in hla_per_group.hla_types:
            if use_high_resolution and hla_type.code.high_res is not None:
                if _recipient_was_tested_for_donor_antigen(antibodies, hla_type.code):
                    continue

                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split]
                positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                if len(positive_tested_antibodies) > 0:
                    if len(tested_antibodies_that_match) == len(positive_tested_antibodies):
                        for match in tested_antibodies_that_match:
                            # HIGH_RES_2
                            positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))
                        continue

                    for match in positive_tested_antibodies:
                        # HIGH_RES_WITH_SPLIT_2
                        positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT))
                    continue

            if hla_type.code.split is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split]
                positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                if len(positive_tested_antibodies) > 0:
                    if (hla_type.code.high_res is None
                            and (len(tested_antibodies_that_match) == len(positive_tested_antibodies))):
                        for match in tested_antibodies_that_match:
                            # HIGH_RES_3
                            positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))
                        continue

                    for match in positive_tested_antibodies:
                        # HIGH_RES_WITH_SPLIT_1
                        positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT))
                    continue

            if hla_type.code.broad is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.broad == antibody.code.broad]
                positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                if len(positive_tested_antibodies) > 0:
                    if (hla_type.code.high_res is None
                            and (len(tested_antibodies_that_match) == len(positive_tested_antibodies))):
                        for match in tested_antibodies_that_match:
                            # HIGH_RES_3
                            positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))
                        continue

                    if hla_type.code.high_res is None and hla_type.code.split is None:
                        for match in positive_tested_antibodies:
                            # HIGH_RES_WITH_BROAD_1
                            positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES_WITH_BROAD))
                        continue

        _add_none_typization(antibodies, positive_matches)
        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, positive_matches))

    return antibody_matches_for_groups


def _do_crossmatch_in_type_b(donor_hla_typing: HLATyping,
                             recipient_antibodies: HLAAntibodies,
                             use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        positive_matches = []
        antibodies = antibodies_per_group.hla_antibody_list

        _add_undecidable_typization(antibodies, hla_per_group, positive_matches)

        for hla_type in hla_per_group.hla_types:
            if use_high_resolution and hla_type.code.high_res is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.high_res == antibody.code.high_res]
                if len(tested_antibodies_that_match) > 0:
                    for match in _get_antibodies_over_cutoff(tested_antibodies_that_match):
                        # HIGH_RES_1
                        positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))
                    continue

            if hla_type.code.split is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split]
                if len(tested_antibodies_that_match) > 0:
                    for match in _get_antibodies_over_cutoff(tested_antibodies_that_match):
                        # SPLIT_1, SPLIT_2
                        positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.SPLIT))
                    continue

            if hla_type.code.broad is not None:
                if hla_type.code.high_res is None and hla_type.code.split is None:  # BROAD_1
                    tested_antibodies_that_match = [antibody for antibody in antibodies
                                                    if hla_type.code.broad == antibody.code.broad]
                else:  # BROAD_2
                    tested_antibodies_that_match = [antibody for antibody in antibodies
                                                    if hla_type.code.broad == antibody.code.broad
                                                    if antibody.code.high_res is None and antibody.code.split is None]
                if len(tested_antibodies_that_match) > 0:
                    for match in _get_antibodies_over_cutoff(tested_antibodies_that_match):
                        positive_matches.append(AntibodyMatch(match, AntibodyMatchTypes.BROAD))
                    continue

        _add_none_typization(antibodies, positive_matches)
        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, positive_matches))

    return antibody_matches_for_groups


def _is_recipient_type_a(recipient_antibodies: HLAAntibodies) -> bool:
    total_antibodies = 0
    is_at_least_one_antibody_below_cutoff = False

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


def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_high_resolution: bool):
    is_type_a = _is_recipient_type_a(recipient_antibodies)

    if is_type_a:
        antibody_matches_for_groups = _do_crossmatch_in_type_a(donor_hla_typing, recipient_antibodies, use_high_resolution)
    else:
        antibody_matches_for_groups = _do_crossmatch_in_type_b(donor_hla_typing, recipient_antibodies, use_high_resolution)

    # Sort antibodies
    for antibodies_per_hla_group in antibody_matches_for_groups:
        antibodies_per_hla_group.antibody_matches = sorted(
            antibodies_per_hla_group.antibody_matches,
            key=lambda hla_group: (
                hla_group.hla_antibody.raw_code,
            ))

    return antibody_matches_for_groups