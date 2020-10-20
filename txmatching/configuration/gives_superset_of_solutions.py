from txmatching.configuration.configuration import Configuration


def _check_if_config_is_supported(configuration: Configuration):
    if not (configuration.solver_constructor_name == 'AllSolutionsSolver'
            and configuration.scorer_constructor_name == 'HLAAdditiveScorer'):
        raise ValueError(f'Unsupported combination '
                         f'({configuration.scorer_constructor_name}, {configuration.solver_constructor_name}) '
                         f'of (scorer, solver)')
