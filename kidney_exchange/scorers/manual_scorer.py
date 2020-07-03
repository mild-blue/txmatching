from typing import Tuple, List

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.additive_scorer import AdditiveScorer


class ManualScorer(AdditiveScorer):
    def __init__(self, additive_scorer: AdditiveScorer, manually_defined_scores: List[Tuple[Donor, Recipient, float]]):
        self._additive_scorer = additive_scorer
        self._manually_defined_scores = manually_defined_scores

    def score_transplant(self, donor: Donor, recipient: Recipient) -> float:
        """
        Returns the manually defined score. If that is not available, then it uses the additive scorer
        """
        raise NotImplementedError("TODO: Implement")  # TODO: Implement
