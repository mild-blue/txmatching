from typing import Iterable

from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.scorers.scorer_constants import HLA_SCORE
from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly


def get_score_for_idx_pairs(compatibility_graph: CompatibilityGraph,
                            pairs: Iterable[DonorRecipientPairIdxOnly]):
    return sum(compatibility_graph[(pair.donor_idx, pair.recipient_idx)][HLA_SCORE] for pair in pairs)
