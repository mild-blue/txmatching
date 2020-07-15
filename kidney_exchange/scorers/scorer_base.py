from typing import Union

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.solvers.matching.matching import Matching

TRANSPLANT_IMPOSSIBLE = "Transplant Impossible"


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
