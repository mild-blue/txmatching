from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass
class CompatibilityInfo:
    scoring_column_to_index: Dict[str, int]
    compatibility_info: Dict[Tuple[int, int], List[int]]
    d_to_r_pairs: Dict[int, int] = None
    non_directed_donors: Iterable[int] = None
