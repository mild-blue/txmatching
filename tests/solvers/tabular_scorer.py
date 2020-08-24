from typing import List, Union

from txmatching.config.configuration import Configuration
from txmatching.patients.donor import Donor
from txmatching.patients.recipient import Recipient
from txmatching.scorers.additive_scorer import AdditiveScorer


class TabularScorer(AdditiveScorer):
    @classmethod
    def from_config(cls, configuration: Configuration) -> 'AdditiveScorer':
        raise NotImplementedError('Will not be implemented for the moment as this class is just for testing')

    def score_transplant_calculated(self, donor: Donor, recipient: Recipient) -> Union[float, str]:
        raise NotImplementedError('Will not be implemented for the moment as this class is just for testing')

    def __init__(self, score_matrix: List[List[float]], donors: List[Donor] = None, recipients: List[Recipient] = None):
        super().__init__()
        self._score_matrix = score_matrix
        self._donors = donors
        self._recipients = recipients

    def score_transplant_ij(self, donor_index: int, recipient_index: int) -> float:
        """
        Useful mainly for testing when we do not care for the patients but we just get the score matrix
        """
        return self._score_matrix[donor_index][recipient_index]

    def score_transplant(self, donor: Donor, recipient: Recipient) -> float:
        index_donor = self._donors.index(donor)
        index_recipient = self._recipients.index(recipient)
        return self.score_transplant_ij(index_donor, index_recipient)
