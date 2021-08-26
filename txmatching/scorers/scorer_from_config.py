from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.high_res_hla_additive_scorer import HighResScorer
from txmatching.scorers.high_res_other_hla_types_additive_scorer import \
    HighResWithDQDPScorer
from txmatching.scorers.split_hla_additive_scorer import SplitScorer
from txmatching.utils.construct_configurable_object import \
    construct_configurable_object
from txmatching.utils.enums import Scorer

SUPPORTED_SCORERS = [SplitScorer, HighResScorer, HighResWithDQDPScorer]


def scorer_from_configuration(config_parameters: ConfigParameters) -> AdditiveScorer:
    # We renamed HLAAdditiveScorer to SplitScorer,
    # If-statement is there for backward compatibility
    if config_parameters.scorer_constructor_name == 'HLAAdditiveScorer':
        config_parameters.scorer_constructor_name = Scorer.SplitScorer

    return construct_configurable_object(
        config_parameters.scorer_constructor_name,
        SUPPORTED_SCORERS,
        config_parameters
    )
