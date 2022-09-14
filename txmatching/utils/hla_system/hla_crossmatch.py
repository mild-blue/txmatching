from dataclasses import dataclass
from typing import List, Set

from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody, HLAType, HLATyping
from txmatching.utils.enums import (AntibodyMatchTypes, HLACrossmatchLevel,
                                    HLAGroup)


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


def _get_antibodies_with_high_res(antibodies: List[HLAAntibody]) -> List[HLAAntibody]:
    return [antibody for antibody in antibodies if antibody.code.high_res]


def _do_crossmatch_in_type_a(hla_types: List[HLAType],
                          antibodies: List[HLAAntibody],
                          use_high_resolution: bool) -> List[AntibodyMatch]:
    matches = []

    for hla_type in hla_types:
        if use_high_resolution and hla_type.code.high_res is not None:
            if hla_type.code in set([antibody.code for antibody in antibodies]):
                continue  # was tested for donor's antigen

            tested_antibodies_that_match = [antibody for antibody in antibodies
                                            if hla_type.code.split == antibody.code.split]
            positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

            if len(positive_tested_antibodies) > 0:
                if len(tested_antibodies_that_match) == len(positive_tested_antibodies):  # all tested antibodies
                    for match in tested_antibodies_that_match:
                        matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))  # HIGH_RES_2
                    continue

                for match in positive_tested_antibodies:
                    matches.append(
                        AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT))  # HIGH_RES_WITH_SPLIT_2
                continue

        if hla_type.code.split is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies
                                            if hla_type.code.split == antibody.code.split]
            positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

            if len(positive_tested_antibodies) > 0:
                if len(tested_antibodies_that_match) == len(
                        positive_tested_antibodies):  # all tested antibodies are positive
                    for match in tested_antibodies_that_match:
                        matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))  # HIGH_RES_3
                    continue

                for match in positive_tested_antibodies:
                    matches.append(
                        AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT))  # HIGH_RES_WITH_SPLIT_1
                continue

        if hla_type.code.broad is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies
                                            if hla_type.code.broad == antibody.code.broad]
            positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

            if len(positive_tested_antibodies) > 0:
                if len(tested_antibodies_that_match) == len(positive_tested_antibodies):  # all tested antibodies are positive
                    for match in tested_antibodies_that_match:
                        matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))  # HIGH_RES_3
                    continue

                for match in positive_tested_antibodies:
                    matches.append(
                        AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT))  # HIGH_RES_WITH_BROAD_1
                continue

    return matches


def _do_crossmatch_in_type_b(hla_types: List[HLAType],
                             antibodies: List[HLAAntibody],
                             use_high_resolution: bool) -> List[AntibodyMatch]:
    matches = []

    for hla_type in hla_types:
        if use_high_resolution and hla_type.code.high_res is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies
                                            if hla_type.code.high_res == antibody.code.high_res]
            if len(tested_antibodies_that_match) > 0:
                for match in _get_antibodies_over_cutoff(tested_antibodies_that_match):
                    # HIGH_RES_1
                    matches.append(AntibodyMatch(match, AntibodyMatchTypes.HIGH_RES))
                continue

        if hla_type.code.split is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies
                                            if hla_type.code.split == antibody.code.split]
            if len(tested_antibodies_that_match) > 0:
                for match in _get_antibodies_over_cutoff(tested_antibodies_that_match):
                    # SPLIT_1, SPLIT_2
                    matches.append(AntibodyMatch(match, AntibodyMatchTypes.SPLIT))
                continue

        if hla_type.code.broad is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies
                                            if hla_type.code.broad == antibody.code.broad]
            if len(tested_antibodies_that_match) > 0:
                for match in _get_antibodies_over_cutoff(tested_antibodies_that_match):
                    # BROAD_1, BROAD_2
                    matches.append(AntibodyMatch(match, AntibodyMatchTypes.BROAD))
                continue

    if len(matches) != len(list(set(matches))):
        raise SystemError("NECO BY MOHLO BYT LEPE")

    return matches


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

    if total_antibodies < 5:
        return False

    if is_at_least_one_antibody_below_cutoff:
        return False

    return True


def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_high_resolution: bool):
    antibody_matches_for_groups = []

    is_type_a = _is_recipient_type_a(recipient_antibodies)

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        antibodies_in_group = antibodies_per_group.hla_antibody_list

        if is_type_a:
            positive_matches = _do_crossmatch_in_type_a(hla_per_group.hla_types, antibodies_in_group, use_high_resolution)
        else:
            positive_matches = _do_crossmatch_in_type_b(hla_per_group.hla_types, antibodies_in_group, use_high_resolution)
        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, positive_matches))

    # Sort antibodies
    for antibodies_per_hla_group in antibody_matches_for_groups:
        antibodies_per_hla_group.antibody_matches = sorted(
            antibodies_per_hla_group.antibody_matches,
            key=lambda hla_group: (
                hla_group.hla_antibody.raw_code,
            ))

    return antibody_matches_for_groups
