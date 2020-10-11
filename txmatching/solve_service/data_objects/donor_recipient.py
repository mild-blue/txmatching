from dataclasses import dataclass


@dataclass
class DonorIdRecipientIdPair:
    donor: int
    recipient: int
