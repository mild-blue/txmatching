from typing import Tuple, List

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient import Patient
from kidney_exchange.patients.recipient import Recipient


class Round:
    """
    A single sequence or cycle of consequtive transplantations
    For example:
    altruist_donor_1 > recipient_2, donor_2 > recipient_3
    donor_1 > recipient_2, donor_1 > recipient_3, donor_3 > recipient_1
    """

    def __init__(self, donor_recipient_list: List[Tuple[Donor, Recipient]]):
        self._donor_recipient_list = donor_recipient_list

    @property
    def length(self) -> int:
        return len(self._donor_recipient_list)

    @property
    def country_count(self) -> int:
        country_codes = set()
        for donor, recipient in self._donor_recipient_list:
            country_codes.add(donor.params.country_code)
            country_codes.add(recipient.params.country_code)

        return len(country_codes)

    def contains_patient(self, patient: Patient) -> bool:
        for donor, recipient in self._donor_recipient_list:
            if patient == donor or patient == recipient:
                return True

        return False
