from typing import List

from kidney_exchange.patients.patient import PatientType
from kidney_exchange.patients.patient_types import DonorRecipientTuple


class TransplantRound:
    """
    A single sequence or cycle of consecutive transplantations
    For example:
    sequence: altruist_donor_1 -> recipient_2, donor_2 -> recipient_3
    cycle: donor_1 -> recipient_2, donor_2 -> recipient_3, donor_3 -> recipient_1
    """

    def __init__(self, donor_recipient_list: List[DonorRecipientTuple]):
        self._donor_recipient_list = donor_recipient_list

    def __str__(self) -> str:
        donor_to_rec_str_list = [f'{donor.medical_id} > {recipient.medical_id}' for donor, recipient in
                                 self._donor_recipient_list]
        str_repr = ','.join(donor_to_rec_str_list)
        return str_repr

    @property
    def length(self) -> int:
        return len(self._donor_recipient_list)

    @property
    def country_count(self) -> int:
        country_codes = set()
        for donor, recipient in self._donor_recipient_list:
            country_codes.add(donor.parameters.country_code)
            country_codes.add(recipient.parameters.country_code)

        return len(country_codes)

    def contains_patient_db_id(self, patient_db_id: int) -> bool:
        for donor, recipient in self._donor_recipient_list:
            if patient_db_id in {donor.db_id, recipient.db_id}:
                return True

        return False

    @property
    def donor_recipient_list(self) -> List[DonorRecipientTuple]:
        return self._donor_recipient_list

    def briding_donor_altruist_or_nothing(self):
        first_donor_type = self._donor_recipient_list[0][0].patient_type
        if first_donor_type == PatientType.BRIDGING_DONOR:
            return 'B'
        elif first_donor_type == PatientType.ALTRUIST:
            return 'A'
        else:
            return ''
