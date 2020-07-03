from kidney_exchange.core.matching import Matching

TRANSPLANT_IMPOSSIBLE = float("-inf")


class ScorerBase:
    def score(self, matching: Matching) -> float:
        """
        Higher score means better matching
        :param matching:
        :return:
        """
        raise NotImplementedError("Has to be overriden")
