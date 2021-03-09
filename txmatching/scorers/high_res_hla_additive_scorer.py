from txmatching.configuration.configuration import Configuration
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.enums import HLAGroup, MatchTypes
from txmatching.utils.hla_system.compatibility_index import CIConfiguration


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

    # TODOO: maybe remove
    def get_max_compatibility_index_for_group(self, hla_group: HLAGroup) -> float:
        return self._hla_typing_bonus_per_groups[hla_group] * 2

    def get_max_compatibility_index(self) -> float:
        return sum(self.get_max_compatibility_index_for_group(hla_group)
                   for hla_group in self._hla_typing_bonus_per_groups.keys())


class HighResHLAAdditiveScorer(HLAAdditiveScorer):

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'HighResHLAAdditiveScorer':
        hla_additive_scorer = HighResHLAAdditiveScorer(configuration)
        return hla_additive_scorer

    @property
    def ci_configuration(self) -> CIConfiguration:
        return HighResHLAAdditiveScorerCIConfiguration()
