from typing import List

import numpy as np

from kidney_exchange.config.configuration import RecipientDonorScore, Configuration
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_base import ScorerBase
from kidney_exchange.solvers.matching.matching import Matching

TRANSPLANT_IMPOSSIBLE = float("-inf")


class AdditiveScorer(ScorerBase):
    def __init__(self, recipient_donor_scores: List[RecipientDonorScore] = None):
        if recipient_donor_scores is not None:
            self._manual_scores = {
                (rec_don_score.donor_id, rec_don_score.recipient_id): rec_don_score.compatibility_index
                for rec_don_score in recipient_donor_scores}
        else:
            self._manual_scores = dict()

    def score_transplant(self, donor: Donor, recipient: Recipient) -> float:
        manual_score = self._manual_scores.get((donor.db_id, recipient.db_id))
        if manual_score is None:
            return self.score_transplant_calculated(donor, recipient)
        else:
            return manual_score

    def score_transplant_calculated(self, donor: Donor, recipient: Recipient) -> float:
        raise NotImplementedError("Has to be overridden")

    def score(self, matching: Matching) -> float:
        """
        Higher score means better matching
        :param matching:
        :return:
        """
        total_score = 0
        for transplant in matching.donor_recipient_list:
            donor, recipient = transplant
            total_score += self.score_transplant(donor=donor, recipient=recipient)

        return total_score

    def get_score_matrix(self, donors: List[Donor], recipients: List[Recipient]) -> np.array:
        score_matrix = np.zeros((len(donors), len(recipients)))
        for donor_index, donor in enumerate(donors):
            for recipient_index, recipient in enumerate(recipients):
                if recipient.related_donor == donor:
                    score = float(np.nan)
                else:
                    score = self.score_transplant(donor, recipient)

                score_matrix[donor_index, recipient_index] = score
        return score_matrix

    @classmethod
    def from_config(cls, configuration: Configuration) -> "AdditiveScorer":
        raise NotImplementedError("Has to be overridden")
