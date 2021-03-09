from txmatching.configuration.configuration import Configuration
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.enums import HLAGroup, MatchTypes
from txmatching.utils.hla_system.compatibility_index import CIConfiguration


class SplitHLAAdditiveScorerCIConfiguration(CIConfiguration):
    _match_type_bonus = {
        MatchTypes.BROAD: 1,
        MatchTypes.SPLIT: 1,
        MatchTypes.HIGH_RES: 1,
        MatchTypes.NONE: 0,
    }
    _hla_typing_bonus_per_groups = {
        HLAGroup.A: 1.0,
        HLAGroup.B: 3.0,
        HLAGroup.DRB1: 9.0,
        HLAGroup.Other: 0.0
    }

    def compute_match_compatibility_index(self, match_type: MatchTypes, hla_group: HLAGroup):
        return self._match_type_bonus[match_type] * self._hla_typing_bonus_per_groups[hla_group]


class SplitHLAAdditiveScorer(HLAAdditiveScorer):

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'SplitHLAAdditiveScorer':
        hla_additive_scorer = SplitHLAAdditiveScorer(configuration)
        return hla_additive_scorer

    @property
    def ci_configuration(self) -> CIConfiguration:
        return SplitHLAAdditiveScorerCIConfiguration()
