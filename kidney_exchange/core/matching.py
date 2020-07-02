from typing import List, Tuple

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient


class Matching:
    def __init__(self, donor_recipient_list: List[Tuple[Donor, Recipient]] = None):
        self._donor_recipient_list = donor_recipient_list

    @property
    def donor_recipient_list(self):
        return self._donor_recipient_list
