from typing import List

from txmatching.patients.patient import DonorType
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair


class TransplantRound:
    """
    A single sequence or cycle of consecutive transplantations
    For example:
    sequence: non_directed_donor_1 -> recipient_2, donor_2 -> recipient_3
    cycle: donor_1 -> recipient_2, donor_2 -> recipient_3, donor_3 -> recipient_1
    """

    def __init__(self, donor_recipient_pairs: List[DonorRecipientPair]):
        self._donor_recipient_pairs = donor_recipient_pairs

    @property
    def length(self) -> int:
        return len(self._donor_recipient_pairs)

    @property
    def country_count(self) -> int:
        country_codes = set()
        for pair in self._donor_recipient_pairs:
            country_codes.add(pair.donor.parameters.country_code)
            country_codes.add(pair.recipient.parameters.country_code)

        return len(country_codes)

    def contains_patient_db_id(self, patient_db_id: int) -> bool:
        for donor, recipient in self._donor_recipient_pairs:
            if patient_db_id in {donor.db_id, recipient.db_id}:
                return True

        return False

    @property
    def donor_recipient_list(self) -> List[DonorRecipientPair]:
        return self._donor_recipient_pairs

    def bridging_donor_non_directed_or_nothing(self):
        first_donor_type = self._donor_recipient_pairs[0].donor.donor_type
        if first_donor_type == DonorType.BRIDGING_DONOR:
            return 'B'
        elif first_donor_type == DonorType.NON_DIRECTED:
            return 'N'
        else:
            return ''
