from kidney_exchange.solvers.matching.matching import Matching


class FilterBase:
    def keep(self, matching: Matching) -> bool:
        raise NotImplementedError("Has to be overriden")
