from typing import Union

from txmatching.config.configuration import Configuration
from txmatching.solvers.matching.matching import Matching


class ScorerBase:
    def score(self, matching: Matching) -> Union[float, str]:
        """
        Higher score means better matching
        :param matching:
        :return:
        """
        raise NotImplementedError("Has to be overridden")

    @classmethod
    def from_config(cls, configuration: Configuration) -> "ScorerBase":
        raise NotImplementedError("Has to be overridden")
