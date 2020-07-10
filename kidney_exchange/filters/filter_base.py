from kidney_exchange.config.configuration import Configuration
from kidney_exchange.solvers.matching.matching import Matching


class FilterBase:
    def keep(self, matching: Matching) -> bool:
        raise NotImplementedError("Has to be overridden")

    @classmethod
    def from_config(cls, configuration: Configuration) -> "FilterBase":
        raise NotImplementedError("Has to be overridden")
