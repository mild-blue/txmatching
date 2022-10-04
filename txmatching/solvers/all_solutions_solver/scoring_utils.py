from typing import Iterable

import numpy as np

from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly


def get_score_for_idx_pairs(score_matrix_array: np.array,
                            pairs: Iterable[DonorRecipientPairIdxOnly]):
    return sum(score_matrix_array[pair.donor_idx, pair.recipient_idx] for pair in pairs)
