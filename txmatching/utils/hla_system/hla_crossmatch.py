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


def _do_crossmatch(matching_antibodies: List[HLAAntibody], positive_matches: Set[AntibodyMatch],
                   _with_type: AntibodyMatchTypes, _type: AntibodyMatchTypes) -> bool:
    if len(matching_antibodies) <= 0:
        return False

    antibodies_over_cutoff = _get_antibodies_over_cutoff(matching_antibodies)
    antibodies_with_high_res = _get_antibodies_with_high_res(matching_antibodies)
    if set(matching_antibodies) == set(antibodies_over_cutoff) == set(antibodies_with_high_res):
        for antibody_over_cutoff in antibodies_over_cutoff:
            positive_matches.add(AntibodyMatch(antibody_over_cutoff, AntibodyMatchTypes.HIGH_RES))
    elif len(_get_antibodies_over_cutoff(antibodies_with_high_res)) > 0:
        for antibody_over_cutoff in antibodies_over_cutoff:
            positive_matches.add(AntibodyMatch(antibody_over_cutoff, _with_type))
    else:
        for antibody_over_cutoff in antibodies_over_cutoff:
            positive_matches.add(AntibodyMatch(antibody_over_cutoff, _type))

    return True


def _do_high_res_crossmatch(hla_type: HLAType, antibodies: List[HLAAntibody],
                            positive_matches: Set[AntibodyMatch]) -> bool:
    matching_antibodies = [antibody for antibody in antibodies
                           if antibody.code.high_res == hla_type.code.high_res]
    return _do_crossmatch(matching_antibodies,
                          positive_matches,
                          _with_type=AntibodyMatchTypes.HIGH_RES,
                          _type=AntibodyMatchTypes.HIGH_RES)


def _do_split_crossmatch(hla_type: HLAType, antibodies: List[HLAAntibody],
                         positive_matches: Set[AntibodyMatch]) -> bool:
    matching_antibodies = [antibody for antibody in antibodies
                           if antibody.code.split == hla_type.code.split]
    return _do_crossmatch(matching_antibodies,
                          positive_matches,
                          _with_type=AntibodyMatchTypes.HIGH_RES_WITH_SPLIT,
                          _type=AntibodyMatchTypes.SPLIT)


def _do_broad_crossmatch(hla_type: HLAType, antibodies: List[HLAAntibody],
                         positive_matches: Set[AntibodyMatch]) -> bool:
    matching_antibodies = [antibody for antibody in antibodies
                           if antibody.code.broad == hla_type.code.broad
                           and (antibody.code.split is None or hla_type.code.split is None)]
    return _do_crossmatch(matching_antibodies,
                          positive_matches,
                          _with_type=AntibodyMatchTypes.HIGH_RES_WITH_BROAD,
                          _type=AntibodyMatchTypes.BROAD)


def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    """Crossmatches between donor's antigens and recipient's antibodies.

    https://github.com/mild-blue/txmatching/tree/master/documentation#types-of-crossmatches-in-txm
    """
    antibody_matches_for_groups = []
    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        assert hla_per_group.hla_group == antibodies_per_group.hla_group

        antibodies: List[HLAAntibody] = antibodies_per_group.hla_antibody_list
        positive_matches: Set[AntibodyMatch] = set()

        # Check for missing typization group in OTHER
        if hla_per_group.hla_group == HLAGroup.Other:
            groups_other = {hla_type.code.group for hla_type in hla_per_group.hla_types}
            for antibody in _get_antibodies_over_cutoff(antibodies):
                if antibody.code.group not in groups_other:
                    positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE))

        # Do all types of crossmatches
        for hla_type in hla_per_group.hla_types:
            if use_high_resolution and hla_type.code.high_res is not None:
                if _do_high_res_crossmatch(hla_type, antibodies, positive_matches):
                    continue

            if hla_type.code.split is not None:
                if _do_split_crossmatch(hla_type, antibodies, positive_matches):
                    continue

            _do_broad_crossmatch(hla_type, antibodies, positive_matches)

        # Add antibodies over cutoff, but with no crossmatch
        antibodies_positive_matches = {match.hla_antibody for match in positive_matches}
        for antibody in _get_antibodies_over_cutoff(antibodies):
            if antibody not in antibodies_positive_matches:
                positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(
            hla_per_group.hla_group,
            list(positive_matches)
        ))

    # Sort antibodies
    for antibodies_per_hla_group in antibody_matches_for_groups:
        antibodies_per_hla_group.antibody_matches = sorted(
            antibodies_per_hla_group.antibody_matches,
            key=lambda hla_group: (
                hla_group.hla_antibody.raw_code,
            ))

    return antibody_matches_for_groups
