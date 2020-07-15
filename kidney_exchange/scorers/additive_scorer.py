from typing import List, Union

from kidney_exchange.config.configuration import RecipientDonorScore, Configuration
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.scorer_base import ScorerBase
from kidney_exchange.solvers.matching.matching import Matching

ORIGINAL_DONOR_RECIPIENT_TUPLE = "Original Donor recipient tuple"

ScoreMatrix = List[List[Union[float, str]]]


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

    def score_transplant_calculated(self, donor: Donor, recipient: Recipient) -> Union[float, str]:
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

    def get_score_matrix(self, donors: List[Donor], recipients: List[Recipient]) -> ScoreMatrix:
        score_matrix = [
            [self._score_transplant_including_original_tuple(donor, recipient) for recipient in recipients]
            for donor in donors
        ]

        return score_matrix

    def _score_transplant_including_original_tuple(self, donor: Donor, recipient: Recipient) -> Union[float, str]:
        if recipient.related_donor == donor:
            score = ORIGINAL_DONOR_RECIPIENT_TUPLE
        else:
            score = self.score_transplant(donor, recipient)
        return score

    @classmethod
    def from_config(cls, configuration: Configuration) -> "AdditiveScorer":
        raise NotImplementedError("Has to be overridden")
