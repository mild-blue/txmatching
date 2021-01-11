from dataclasses import dataclass
from typing import Iterable

from txmatching.configuration.configuration import Configuration
from txmatching.scorers.score_matrix import ScoreMatrix
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


@dataclass
class PairingResult:
    txm_event_db_id: int
    configuration: Configuration
    score_matrix: ScoreMatrix
    calculated_matchings: Iterable[MatchingWithScore]
    all_results_found: bool
