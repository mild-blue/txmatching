from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass
class DonorRecipientPairIdxOnly:
    donor_idx: int
    recipient_idx: int


def get_score_for_idx_pairs(score_matrix_array: np.array,
                            pairs: Iterable[DonorRecipientPairIdxOnly]):
    return sum([score_matrix_array[pair.donor_idx, pair.recipient_idx] for pair in pairs])
