from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_base import ScorerBase
from kidney_exchange.solvers.matching.matching import Matching


class AdditiveScorer(ScorerBase):
    def _score_transplant(self, donor: Donor, recipient: Recipient) -> float:
        raise NotImplementedError("Has to be overriden")

    def score(self, matching: Matching) -> float:
        total_score = 0
        for transplant in matching.donor_recipient_list:
            donor, recipient = transplant
            total_score += self._score_transplant(donor=donor, recipient=recipient)

        return total_score
