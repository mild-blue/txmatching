from dataclasses import dataclass
from typing import List

from txmatching.configuration.configuration import Configuration
from txmatching.scorers.score_matrix import ScoreMatrix
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


@dataclass
class PairingResult:
    txm_event_db_id: int
    configuration: Configuration
    score_matrix: ScoreMatrix
    calculated_matchings_list: List[MatchingWithScore]
    found_matchings_count: int
    all_results_found: bool
