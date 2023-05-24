from dataclasses import dataclass
from typing import List

from txmatching.utils.enums import HLA_GROUPS, HLAGroup
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, HLAMatch)
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatch, AntibodyMatchForHLAGroup)


@dataclass
class DetailedScoreForHLAGroup:
    hla_group: HLAGroup
    donor_matches: List[HLAMatch]
    recipient_matches: List[HLAMatch]
    group_compatibility_index: float
    antibody_matches: List[AntibodyMatch]


def get_detailed_score(compatibility_index_detailed: List[DetailedCompatibilityIndexForHLAGroup],
                       antibodies: List[AntibodyMatchForHLAGroup]) -> List[DetailedScoreForHLAGroup]:
    assert len(antibodies) == len(compatibility_index_detailed), (
        'Antibodies and compatibility_index_detailed do not contain the same hla groups. '
        'This is unexpected and should never happen. '
        f'Both should contain these hla groups (in this order): {HLA_GROUPS + [HLAGroup.INVALID_CODES]}.')
    detailed_scores = []
    for antibody_group, compatibility_index_detailed_group in zip(antibodies, compatibility_index_detailed):
        assert antibody_group.hla_group == compatibility_index_detailed_group.hla_group, (
            'Antibodies and compatibility_index_detailed contain hla groups in different order. '
            'This is unexpected and should never happen.')
        if not (len(compatibility_index_detailed_group.recipient_matches) == 0 and len(
                compatibility_index_detailed_group.donor_matches) == 0 and len(antibody_group.antibody_matches) == 0):
            detailed_scores.append(
                DetailedScoreForHLAGroup(
                    recipient_matches=compatibility_index_detailed_group.recipient_matches,
                    hla_group=compatibility_index_detailed_group.hla_group,
                    group_compatibility_index=compatibility_index_detailed_group.group_compatibility_index,
                    antibody_matches=antibody_group.antibody_matches,
                    donor_matches=compatibility_index_detailed_group.donor_matches
                )
            )
    return detailed_scores
