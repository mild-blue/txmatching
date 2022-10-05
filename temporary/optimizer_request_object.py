from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Pair:
    donor_id: int
    recipient_id: Optional[int] = None


@dataclass
class OptimizerConfiguration:
    objective: List[Dict[int, int]]
    max_cycle_length: Optional[int] = 4
    max_chain_length: Optional[int] = 4


@dataclass
class CompatibilityGraphEntry:
    donor_id: int
    recipient_id: int
    weights: Dict[str, int]


@dataclass
class OptimizerRequest:
    compatibility_graph: List[CompatibilityGraphEntry]
    pairs: List[Pair]
    settings: OptimizerConfiguration
