from dataclasses import dataclass
from typing import List

from txmatching.patients.patient import DonorType
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair


@dataclass
class TransplantRound:
    """
    A single sequence or cycle of consecutive transplantations
    For example:
    sequence: non_directed_donor_1 -> recipient_2, donor_2 -> recipient_3
    cycle: donor_1 -> recipient_2, donor_2 -> recipient_3, donor_3 -> recipient_1
    """

    donor_recipient_pairs: List[DonorRecipientPair]

    def __post_init__(self):
        if len(self.donor_recipient_pairs) == 0:
            raise AssertionError('Number of Transplants in a cycle must be non-empty')

    def length(self) -> int:
        return len(self.donor_recipient_pairs)

    def country_count(self) -> int:
        country_codes = set()
        for pair in self.donor_recipient_pairs:
            country_codes.add(pair.donor.parameters.country_code)
            country_codes.add(pair.recipient.parameters.country_code)

        return len(country_codes)

    def contains_patient_db_id(self, patient_db_id: int) -> bool:
        for pair in self.donor_recipient_pairs:
            if patient_db_id in {pair.donor.db_id, pair.recipient.db_id}:
                return True

        return False

    def bridging_donor_non_directed_or_nothing(self):
        first_donor_type = self.donor_recipient_pairs[0].donor.donor_type
        if first_donor_type == DonorType.BRIDGING_DONOR:
            return 'B'
        elif first_donor_type == DonorType.NON_DIRECTED:
            return 'N'
        else:
            return ''
