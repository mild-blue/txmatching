from kidney_exchange.config.configuration import Configuration
from kidney_exchange.scorers.hla_additive_scorer import HLAAdditiveScorer
from kidney_exchange.scorers.scorer_base import ScorerBase

_supported_scorers = [HLAAdditiveScorer]


def make_scorer_from_config(configuration: Configuration) -> ScorerBase:
    scorer_name_to_scorer_constructor = {scorer.__name__: scorer for scorer in _supported_scorers}
    scorer_constructor = scorer_name_to_scorer_constructor.get(configuration.scorer_constructor_name)

    if scorer_constructor is None:
        raise NotImplementedError(f"Scorer {configuration.scorer_constructor_name} not supported yet")

    scorer = scorer_constructor.from_config(configuration)

    return scorer


if __name__ == "__main__":
    config = Configuration()
    scorer_made_from_config = make_scorer_from_config(config)
    print(scorer_made_from_config)
