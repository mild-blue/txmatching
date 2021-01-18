from dataclasses import dataclass
from typing import Dict

from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel


@dataclass
class DatabasePairingResult:
    score_matrix: Dict
    matchings: MatchingsModel
