from typing import Dict

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.solvers.matching.matching import Matching


class ScorerBase:
    def score(self, matching: Matching, donors_dict: Dict, recipients_dict: Dict) -> float:
        """
        Higher score means better matching
        """
        raise NotImplementedError('Has to be overridden')

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'ScorerBase':
        raise NotImplementedError('Has to be overridden')
