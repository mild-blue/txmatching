from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DonorToRecipient:
    donor_id: int
    recipient_id: int
    score: List[int]


@dataclass
class OptimizerReturn:
    cycles_and_chains: List[List[DonorToRecipient]]
    statistics: Dict[str, int]
