from dataclasses import dataclass
from typing import List

from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody, HLATyping
from txmatching.utils.enums import AntibodyMatchTypes, HLAGroup
from txmatching.utils.hla_system.hla_transformations import (broad_to_split,
                                                             split_to_broad)


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
                               use_split_resolution: bool) -> bool:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    e.g. A23 -> A23 True
         A9 -> A9  True
         A23 -> A9 True
         A23 -> A24 False if use_split_resolution else True
         A9 -> A23 True
         A9 broad <=> A23, A24 split
    :param donor_hla_typing: donor hla_typing to crossmatch
    :param recipient_antibodies: recipient antibodies to crossmatch
    :param use_split_resolution: setting whether to use split resolution for crossmatch determination
    :return:
    """
    common_codes = {code.hla_antibody for code_group in
                    get_crossmatched_antibodies(donor_hla_typing, recipient_antibodies, use_split_resolution) for code
                    in code_group.antibody_matches if code.match_type is not AntibodyMatchTypes.NONE}
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_split_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches = []
    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups_over_cutoff):
        assert hla_per_group.hla_group == antibodies_per_group.hla_group
        recipient_antibodies_set = set()
        if use_split_resolution:
            # in case some code is in broad resolution we treat it is as if all split resolution codes were present
            donor_hla_typing_set = {split_code for hla in
                                    hla_per_group.hla_types for split_code in
                                    broad_to_split(hla.code.split_or_broad)}

            for antibody in antibodies_per_group.hla_antibody_list:
                if set(broad_to_split(antibody.code.split_or_broad)).intersection(donor_hla_typing_set):
                    recipient_antibodies_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.MATCH))
                else:
                    recipient_antibodies_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))

        else:
            donor_hla_typing_set = {code.code.broad for code in hla_per_group.hla_types}
            for antibody in antibodies_per_group.hla_antibody_list:
                if antibody.code.broad in donor_hla_typing_set:
                    recipient_antibodies_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.MATCH))
                else:
                    recipient_antibodies_set.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))

        antibody_matches.append(AntibodyMatchForHLAGroup(
            hla_per_group.hla_group,
            list(recipient_antibodies_set)
        ))

    return antibody_matches
