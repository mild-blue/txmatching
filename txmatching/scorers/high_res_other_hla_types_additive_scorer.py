from txmatching.configuration.configuration import Configuration
from txmatching.scorers.high_res_hla_additive_scorer import (
    EQUAL_BONUS_PER_GROUPS, PROPOSED_MATCH_TYPE_BONUS)
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.hla_system.compatibility_index import CIConfiguration


# this class serves as configuration of the scorer and the the few methods are meaningful here
# pylint: disable=too-few-public-methods
class HighResOtherHLATypesHLAAdditiveScorerCIConfiguration(CIConfiguration):
    @property
    def match_type_bonus(self):
        return PROPOSED_MATCH_TYPE_BONUS

    @property
    def hla_typing_bonus_per_groups(self):
        return EQUAL_BONUS_PER_GROUPS


class HighResWithDQDPScorer(HLAAdditiveScorer):

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'HighResWithDQDPScorer':
        hla_additive_scorer = HighResWithDQDPScorer(configuration)
        return hla_additive_scorer

    @property
    def ci_configuration(self) -> CIConfiguration:
        return HighResOtherHLATypesHLAAdditiveScorerCIConfiguration()
