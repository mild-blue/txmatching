from dataclasses import dataclass
from typing import List, Set

from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody, HLATyping
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


# Many branches make sense here
# pylint: disable=too-many-branches
def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []
    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        assert hla_per_group.hla_group == antibodies_per_group.hla_group

        antibodies = antibodies_per_group.hla_antibody_list
        positive_matches = set()  # type: Set[AntibodyMatch]

        # check for missing typization group
        if hla_per_group.hla_types == []:
            for antibody in antibodies:
                positive_matches.add(
                        AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE))

        for hla_type in hla_per_group.hla_types:
            # check high res crossmatch
            if use_high_resolution and hla_type.code.high_res is not None:
                matching_antibodies = [antibody for antibody in antibodies
                                       if antibody.code.high_res == hla_type.code.high_res]
                if len(matching_antibodies) > 0:
                    assert len(matching_antibodies) == 1, 'due to parsing, each antibody should be unique'
                    for antibody_over_cutoff in _get_antibodies_over_cutoff(matching_antibodies):
                        positive_matches.add(AntibodyMatch(antibody_over_cutoff, AntibodyMatchTypes.HIGH_RES))
                    continue
            # check split crossmatch
            if hla_type.code.split is not None:
                matching_antibodies = [antibody for antibody in antibodies
                                       if antibody.code.split == hla_type.code.split]
                antibodies_without_split = [antibody for antibody in antibodies
                                       if not antibody.code.split]
                for antibody_without_split in antibodies_without_split:
                    positive_matches.add(
                                AntibodyMatch(antibody_without_split, AntibodyMatchTypes.ANTIBODIES_MISSING))
                if len(matching_antibodies) > 0:
                    antibodies_over_cutoff = _get_antibodies_over_cutoff(matching_antibodies)
                    antibodies_with_high_res = _get_antibodies_with_high_res(matching_antibodies)
                    if set(matching_antibodies) == set(antibodies_over_cutoff) == set(antibodies_with_high_res):
                        for antibody_over_cutoff in antibodies_over_cutoff:
                            positive_matches.add(
                                AntibodyMatch(antibody_over_cutoff, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT))
                    else:
                        for antibody_over_cutoff in antibodies_over_cutoff:
                            positive_matches.add(AntibodyMatch(antibody_over_cutoff, AntibodyMatchTypes.SPLIT))
                    continue
            # check broad crossmatch
            matching_antibodies = [antibody for antibody in antibodies
                                   if antibody.code.broad == hla_type.code.broad
                                   and (antibody.code.split is None
                                        or hla_type.code.split is None)]
            antibodies_without_broad = [antibody for antibody in antibodies
                                       if not antibody.code.broad]
            for antibody_without_broad in antibodies_without_broad:
                positive_matches.add(
                            AntibodyMatch(antibody_without_broad, AntibodyMatchTypes.ANTIBODIES_MISSING))
            if len(matching_antibodies) > 0:
                antibodies_over_cutoff = _get_antibodies_over_cutoff(matching_antibodies)
                antibodies_with_high_res = _get_antibodies_with_high_res(matching_antibodies)
                if set(matching_antibodies) == set(antibodies_over_cutoff) == set(antibodies_with_high_res):
                    for antibody_over_cutoff in antibodies_over_cutoff:
                        positive_matches.add(
                            AntibodyMatch(antibody_over_cutoff, AntibodyMatchTypes.HIGH_RES_WITH_BROAD))
                else:
                    for antibody_over_cutoff in antibodies_over_cutoff:
                        positive_matches.add(AntibodyMatch(antibody_over_cutoff, AntibodyMatchTypes.BROAD))

        # Construct antibody matches set
        antibody_matches_set = set()
        for antibody in _get_antibodies_over_cutoff(antibodies):
            if AntibodyMatch(antibody, AntibodyMatchTypes.HIGH_RES) in positive_matches:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.HIGH_RES))
            elif AntibodyMatch(antibody, AntibodyMatchTypes.SPLIT) in positive_matches:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.SPLIT))
            elif AntibodyMatch(antibody, AntibodyMatchTypes.BROAD) in positive_matches:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.BROAD))
            elif AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE) in positive_matches:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE))
            elif AntibodyMatch(antibody, AntibodyMatchTypes.ANTIBODIES_MISSING) in positive_matches:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.ANTIBODIES_MISSING))
            elif AntibodyMatch(antibody, AntibodyMatchTypes.HIGH_RES_WITH_BROAD) in positive_matches:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.HIGH_RES_WITH_BROAD))
            elif AntibodyMatch(antibody, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT) in positive_matches:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT))
            else:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(
            hla_per_group.hla_group,
            list(antibody_matches_set)
        ))

    # Sort antibodies
    for antibodies_per_hla_group in antibody_matches_for_groups:
        antibodies_per_hla_group.antibody_matches = sorted(
            antibodies_per_hla_group.antibody_matches,
            key=lambda hla_group: (
                hla_group.hla_antibody.raw_code,
            ))

    return antibody_matches_for_groups
