from dataclasses import dataclass
from typing import List

from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody, HLATyping
from txmatching.utils.enums import AntibodyMatchTypes, HLAGroup


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
                               use_high_res_resolution: bool) -> bool:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    e.g. A23 -> A23 True
         A9 -> A9  True
         A23 -> A9 True
         A23 -> A24 False if use_high_res_resolution else True
         A9 -> A23 True
         A9 broad <=> A23, A24 split
    :param donor_hla_typing: donor hla_typing to crossmatch
    :param recipient_antibodies: recipient antibodies to crossmatch
    :param use_high_res_resolution: setting whether to high res resolution for crossmatch determination
    :return:
    """
    common_codes = {antibody_match.hla_antibody for antibody_match_group in
                    get_crossmatched_antibodies(donor_hla_typing, recipient_antibodies, use_high_res_resolution)
                    for antibody_match in antibody_match_group.antibody_matches
                    if antibody_match.match_type is not AntibodyMatchTypes.NONE}
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


def _get_antibodies_over_cutoff(antibodies: List[HLAAntibody]) -> List[HLAAntibody]:
    return [antibody for antibody in antibodies if antibody.mfi >= antibody.cutoff]


# Many branches make sense here
# pylint: disable=too-many-branches
def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_high_res_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []
    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        assert hla_per_group.hla_group == antibodies_per_group.hla_group

        antibodies = antibodies_per_group.hla_antibody_list
        positive_match_antibodies = set()

        for hla_type in hla_per_group.hla_types:
            # check high res crossmatch
            if use_high_res_resolution and hla_type.code.high_res is not None:
                matching_antibodies = [antibody for antibody in antibodies
                                       if antibody.code.high_res == hla_type.code.high_res]
                if len(matching_antibodies) > 0:
                    for antibody_over_cutoff in _get_antibodies_over_cutoff(matching_antibodies):
                        positive_match_antibodies.add(antibody_over_cutoff)
                    continue
            # check split crossmatch
            if hla_type.code.split is not None:
                matching_antibodies = [antibody for antibody in antibodies
                                       if antibody.code.split == hla_type.code.split]
                if len(matching_antibodies) > 0:
                    for antibody_over_cutoff in _get_antibodies_over_cutoff(matching_antibodies):
                        positive_match_antibodies.add(antibody_over_cutoff)
                    continue
            # check broad crossmatch
            matching_antibodies = [antibody for antibody in antibodies
                                   if antibody.code.broad == hla_type.code.broad
                                   and (antibody.code.split is None
                                        or hla_type.code.split is None)]
            if len(matching_antibodies) > 0:
                for antibody_over_cutoff in _get_antibodies_over_cutoff(matching_antibodies):
                    positive_match_antibodies.add(antibody_over_cutoff)

        # Construct antibody matches set
        antibody_matches_set = set()
        for antibody in antibodies:
            if antibody in positive_match_antibodies:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.MATCH))
            else:
                antibody_matches_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(
            hla_per_group.hla_group,
            list(antibody_matches_set)
        ))

    return antibody_matches_for_groups
