from dataclasses import dataclass


@dataclass
class DonorRecipientModel:
    donor: int
    recipient: int
