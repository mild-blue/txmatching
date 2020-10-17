from dataclasses import dataclass


@dataclass
class DonorRecipientDTO:
    donor: int
    recipient: int
