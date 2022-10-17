from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.filters.filter_base import FilterBase
from txmatching.solvers.matching.matching import Matching


@dataclass
class FilterDefault(FilterBase):
    configuration: ConfigParameters

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'FilterBase':
        return FilterDefault(config_parameters)

    def keep(self, matching: Matching) -> bool:
        return True
