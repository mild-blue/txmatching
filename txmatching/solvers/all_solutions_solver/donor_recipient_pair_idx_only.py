from dataclasses import dataclass


@dataclass
class DonorRecipientPairIdxOnly:
    donor_idx: int
    recipient_idx: int
