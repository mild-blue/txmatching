from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.enums import HLAGroup, MatchType
from txmatching.utils.hla_system.compatibility_index import CIConfiguration

PROPOSED_MATCH_TYPE_BONUS = {
    MatchType.BROAD: 1,
    MatchType.SPLIT: 2,
    MatchType.HIGH_RES: 3,
    MatchType.NONE: 0,
}

EQUAL_BONUS_PER_GROUPS = {
    HLAGroup.A: 1,
    HLAGroup.B: 1,
    HLAGroup.DRB1: 1,
    HLAGroup.CW: 1,
    HLAGroup.DPA: 1,
    HLAGroup.DPB: 1,
    HLAGroup.DQA: 1,
    HLAGroup.DQB: 1,
    HLAGroup.OTHER_DR: 1
}


# this class serves as configuration of the scorer the few methods are meaningful here
# pylint: disable=too-few-public-methods
class HighResScorerCIConfiguration(CIConfiguration):
    @property
    def match_type_bonus(self):
        return PROPOSED_MATCH_TYPE_BONUS

    @property
    def hla_typing_bonus_per_groups(self):
        bonus = EQUAL_BONUS_PER_GROUPS.copy()
        return bonus


class HighResScorer(HLAAdditiveScorer):

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'HighResScorer':
        hla_additive_scorer = HighResScorer(config_parameters)
        return hla_additive_scorer

    @property
    def ci_configuration(self) -> CIConfiguration:
        return HighResScorerCIConfiguration()
