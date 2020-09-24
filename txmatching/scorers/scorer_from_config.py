from txmatching.configuration.configuration import Configuration
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.construct_configurable_object import construct_configurable_object

_supported_scorers = [HLAAdditiveScorer]


def scorer_from_configuration(configuration: Configuration) -> AdditiveScorer:
    return construct_configurable_object(configuration.scorer_constructor_name, _supported_scorers, configuration)
