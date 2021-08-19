from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.solvers.matching.matching import Matching


class FilterBase:
    def keep(self, matching: Matching) -> bool:
        raise NotImplementedError('Has to be overridden')

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'FilterBase':
        raise NotImplementedError('Has to be overridden')
