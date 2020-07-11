from kidney_exchange.config.configuration import Configuration
from kidney_exchange.scorers.hla_additive_scorer import HLAAdditiveScorer
from kidney_exchange.scorers.scorer_base import ScorerBase
from kidney_exchange.utils.construct_configurable_object import construct_configurable_object

_supported_scorers = [HLAAdditiveScorer]


def scorer_from_configuration(config: Configuration) -> ScorerBase:
    return construct_configurable_object(config.scorer_constructor_name, _supported_scorers, config)
