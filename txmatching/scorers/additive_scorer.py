from typing import List, Union

from txmatching.config.configuration import DonorRecipientScore, Configuration
from txmatching.patients.donor import Donor
from txmatching.patients.recipient import Recipient
from txmatching.scorers.scorer_base import ScorerBase
from txmatching.solvers.matching.matching import Matching

ORIGINAL_DONOR_RECIPIENT_TUPLE = "Original Donor recipient tuple"
TRANSPLANT_IMPOSSIBLE = "Transplant Impossible"

ScoreMatrix = List[List[Union[float, str]]]


class AdditiveScorer(ScorerBase):
    def __init__(self, manual_donor_recipient_scores: List[DonorRecipientScore] = None):
        if manual_donor_recipient_scores is not None:
            self._manual_donor_recipient_scores = {
                (don_rec_score.donor_id, don_rec_score.recipient_id): don_rec_score.score
                for don_rec_score in manual_donor_recipient_scores}
        else:
            self._manual_donor_recipient_scores = dict()

    def score_transplant(self, donor: Donor, recipient: Recipient) -> float:
        manual_score = self._manual_donor_recipient_scores.get((donor.db_id, recipient.db_id))
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
        score_matrix = [[self._score_transplant_including_original_tuple(donor, recipient)
                         for recipient in recipients]
                        for donor in donors]

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
