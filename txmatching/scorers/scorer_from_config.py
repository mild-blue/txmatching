from txmatching.configuration.configuration import Configuration
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.high_res_hla_additive_scorer import HighResScorer
from txmatching.scorers.high_res_other_hla_types_additive_scorer import \
    HighResWithDQDPScorer
from txmatching.scorers.split_hla_additive_scorer import SplitScorer
from txmatching.utils.construct_configurable_object import \
    construct_configurable_object

SUPPORTED_SCORERS = [SplitScorer, HighResScorer, HighResWithDQDPScorer]


def scorer_from_configuration(configuration: Configuration) -> AdditiveScorer:
    # We renamed HLAAdditiveScorer to SplitScorer
    if configuration.scorer_constructor_name == 'HLAAdditiveScorer':
        configuration.scorer_constructor_name = 'SplitScorer'

    return construct_configurable_object(configuration.scorer_constructor_name, SUPPORTED_SCORERS, configuration)
