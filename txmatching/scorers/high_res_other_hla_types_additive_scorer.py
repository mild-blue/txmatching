from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.enums import HLAGroup, MatchType
from txmatching.utils.hla_system.compatibility_index import CIConfiguration


# this class serves as configuration of the scorer and the the few methods are meaningful here
# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
class HighResOtherHLATypesHLAAdditiveScorerCIConfiguration(CIConfiguration):

    @property
    def match_type_bonus(self):
        return {
            MatchType.BROAD: 1,
            MatchType.SPLIT: 2,
            MatchType.HIGH_RES: 3,
            MatchType.NONE: 0,
        }

    @property
    def hla_typing_bonus_per_groups_without_dp_dq(self):
        return {
            HLAGroup.A: 1,
            HLAGroup.B: 1,
            HLAGroup.DRB1: 1,
            HLAGroup.CW: 0,
            HLAGroup.OTHER_DR: 0
        }

    @property
    def hla_typing_bonus_per_dp_dq(self):
        return {
            'DPA': 0,
            'DPB': 0,
            'DQA': 0,
            'DQB': 0
        }

class HighResWithDQDPScorer(HLAAdditiveScorer):

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'HighResWithDQDPScorer':
        hla_additive_scorer = HighResWithDQDPScorer(config_parameters)
        return hla_additive_scorer

    @property
    def ci_configuration(self) -> CIConfiguration:
        return HighResOtherHLATypesHLAAdditiveScorerCIConfiguration()
