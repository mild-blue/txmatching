from dataclasses import dataclass
from typing import List

from txmatching.patients.patient_parameters import HLAAntibodies, HLATyping
from txmatching.utils.enums import AntibodyMatchTypes, HLAGroups
from txmatching.utils.hla_system.hla_transformations import (broad_to_split,
                                                             split_to_broad)


@dataclass(eq=True, frozen=True)
class AntibodyMatch:
    hla_code: str
    match_type: AntibodyMatchTypes



@dataclass
class AntibodyMatchForHLAGroup:
    hla_group: HLAGroups
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
    common_codes = {code.hla_code for code_group in
                    get_crossmatched_antibodies(donor_hla_typing, recipient_antibodies, use_split_resolution) for code
                    in code_group.antibody_matches if code.match_type is not AntibodyMatchTypes.NONE}
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_split_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches = []
    for code_group_typing, code_group_antibodies in zip(donor_hla_typing.codes_per_group,
                                                        recipient_antibodies.hla_codes_over_cutoff_per_group):
        assert code_group_typing.hla_group == code_group_antibodies.hla_group
        recipient_antibodies_set = set()
        if use_split_resolution:
            # in case some code is in broad resolution we treat it is as if all split resolution codes were present
            donor_hla_typing_set = {split_code for code in
                                    code_group_typing.hla_codes for split_code in
                                    broad_to_split(code)}

            for code in code_group_antibodies.hla_codes:
                if set(broad_to_split(code)).intersection(donor_hla_typing_set):
                    recipient_antibodies_set.add(AntibodyMatch(code, AntibodyMatchTypes.MATCH))
                else:
                    recipient_antibodies_set.add(AntibodyMatch(code, AntibodyMatchTypes.NONE))

        else:
            donor_hla_typing_set = {split_to_broad(code) for code in code_group_typing.hla_codes}
            for code in code_group_antibodies.hla_codes:
                if split_to_broad(code) in donor_hla_typing_set:
                    recipient_antibodies_set.add(AntibodyMatch(code, AntibodyMatchTypes.MATCH))
                else:
                    recipient_antibodies_set.add(AntibodyMatch(code, AntibodyMatchTypes.NONE))

        antibody_matches.append(AntibodyMatchForHLAGroup(
            code_group_typing.hla_group,
            list(recipient_antibodies_set)
        ))

    return antibody_matches
