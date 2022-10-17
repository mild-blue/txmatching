from typing import FrozenSet, Set, Tuple

from txmatching.solvers.donor_recipient_pair import DonorRecipientPair

BEST_SOLUTION_use_high_resolution_TRUE = {(26, 11), (38, 14), (13, 29), (37, 25), (22, 16), (17, 24), (36, 21)}
# Chains in solution
# 37, 25; 26, 11
# 36, 21; 22, 16; 17, 24
# 38, 14;
# 13, 29;


# Donor Ids in solution
# 37, 26; 26, 11
# 36, 22; 22, 16; 17, 25
# 38, 15;
# 13, 30;

# Donor idx with chain idx in solution
# 36, 25; 25, 10 - 15
# 35, 21; 21, 16; 16, 24 - 42
# 37, 14; - 37
# 12, 29; - 26

def get_donor_recipient_pairs_from_solution(matching_pairs: FrozenSet[DonorRecipientPair]) -> Set[Tuple[int, int]]:
    matching_pairs_db_ids = set()
    for pair in matching_pairs:
        matching_pairs_db_ids.add((pair.donor.db_id, pair.recipient.db_id))
    return matching_pairs_db_ids
