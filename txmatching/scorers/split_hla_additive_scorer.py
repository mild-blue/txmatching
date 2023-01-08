from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.enums import HLAGroup, MatchType
from txmatching.utils.hla_system.compatibility_index import CIConfiguration


# pylint: disable=too-few-public-methods
class SplitScorerCIConfiguration(CIConfiguration):

    @property
    def match_type_bonus(self):
        return {
            MatchType.BROAD: 1,
            MatchType.SPLIT: 1,
            MatchType.HIGH_RES: 1,
            MatchType.NONE: 0,
        }

    @property
    def hla_typing_bonus_per_groups(self):
        return {
            HLAGroup.A: 1,
            HLAGroup.B: 3,
            HLAGroup.DRB1: 9,
            HLAGroup.CW: 1,
            HLAGroup.DPA: 1,
            HLAGroup.DPB: 1,
            HLAGroup.DQA: 1,
            HLAGroup.DQB: 1,
            HLAGroup.OTHER_DR: 1
        }


class SplitScorer(HLAAdditiveScorer):

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'SplitScorer':
        hla_additive_scorer = SplitScorer(config_parameters)
        return hla_additive_scorer

    @property
    def ci_configuration(self) -> CIConfiguration:
        return SplitScorerCIConfiguration()
