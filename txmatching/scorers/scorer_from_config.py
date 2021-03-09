from txmatching.configuration.configuration import Configuration
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.high_res_hla_additive_scorer import \
    HighResHLAAdditiveScorer
from txmatching.scorers.split_hla_additive_scorer import SplitHLAAdditiveScorer
from txmatching.utils.construct_configurable_object import \
    construct_configurable_object

_supported_scorers = [SplitHLAAdditiveScorer, HighResHLAAdditiveScorer]


def scorer_from_configuration(configuration: Configuration) -> AdditiveScorer:
    # We renamed HLAAdditiveScorer to SplitHLAAdditiveScorer
    if configuration.scorer_constructor_name == 'HLAAdditiveScorer':
        configuration.scorer_constructor_name = 'SplitHLAAdditiveScorer'

    return construct_configurable_object(configuration.scorer_constructor_name, _supported_scorers, configuration)
