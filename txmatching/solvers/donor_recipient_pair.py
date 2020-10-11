from dataclasses import dataclass

from txmatching.patients.patient import Donor, Recipient


@dataclass
class DonorRecipientPair:
    donor: Donor
    recipient: Recipient

    def __hash__(self):
        return (self.donor.db_id, self.recipient.db_id).__hash__()
