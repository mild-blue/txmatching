from dataclasses import dataclass
from typing import List, Optional

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.scorers.score_matrix import ScoreMatrix
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


@dataclass
class PairingResult:
    txm_event_db_id: int
    configuration: ConfigParameters
    score_matrix: ScoreMatrix
    calculated_matchings_list: List[MatchingWithScore]
    found_matchings_count: Optional[int]
    all_results_found: bool
