from txmatching.configuration.configuration import Configuration
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.enums import HLAGroup, MatchTypes
from txmatching.utils.hla_system.compatibility_index import CIConfiguration


# pylint: disable=too-few-public-methods
class HighResHLAAdditiveScorerCIConfiguration(CIConfiguration):
    _match_type_bonus = {
        MatchTypes.BROAD: 1,
        MatchTypes.SPLIT: 2,
        MatchTypes.HIGH_RES: 3,
        MatchTypes.NONE: 0,
    }
    _hla_typing_bonus_per_groups = {
        HLAGroup.A: 1.0,
        HLAGroup.B: 1.0,
        HLAGroup.DRB1: 1.0,
        HLAGroup.Other: 0.0
    }

    def compute_match_compatibility_index(self, match_type: MatchTypes, hla_group: HLAGroup):
        return self._match_type_bonus[match_type] * self._hla_typing_bonus_per_groups[hla_group]


class HighResHLAAdditiveScorer(HLAAdditiveScorer):

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'HighResHLAAdditiveScorer':
        hla_additive_scorer = HighResHLAAdditiveScorer(configuration)
        return hla_additive_scorer

    @property
    def ci_configuration(self) -> CIConfiguration:
        return HighResHLAAdditiveScorerCIConfiguration()
