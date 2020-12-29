from dataclasses import dataclass

from typing import List

from txmatching.utils.enums import HLAGroup
from txmatching.utils.hla_system.compatibility_index import HLAMatch
from txmatching.utils.hla_system.hla_crossmatch import AntibodyMatch


@dataclass
class DetailedScoreForHLAGroup:
    hla_group: HLAGroup
    donor_matches: List[HLAMatch]
    recipient_matches: List[HLAMatch]
    group_compatibility_index: float
    antibody_matches: List[AntibodyMatch]
