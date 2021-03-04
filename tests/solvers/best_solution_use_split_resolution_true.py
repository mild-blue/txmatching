from typing import FrozenSet, Set, Tuple

from txmatching.solvers.donor_recipient_pair import DonorRecipientPair

BEST_SOLUTION_use_high_res_resolution_TRUE = {(26, 11), (38, 14), (13, 29), (37, 25), (22, 16), (17, 24), (36, 21)}


def get_donor_recipient_pairs_from_solution(matching_pairs: FrozenSet[DonorRecipientPair]) -> Set[Tuple[int, int]]:
    matching_pairs_db_ids = set()
    for pair in matching_pairs:
        matching_pairs_db_ids.add((pair.donor.db_id, pair.recipient.db_id))
    return matching_pairs_db_ids
