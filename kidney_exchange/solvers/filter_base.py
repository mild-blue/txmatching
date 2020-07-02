from kidney_exchange.core.matching import Matching


class FilterBase:
    def keep(self, matching: Matching) -> bool:
        raise NotImplementedError("Has to be overriden")
