from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Pair:
    donor_id: int
    recipient_id: Optional[int] = None
    category: Optional[str] = None


@dataclass
class Limitations:
    max_cycle_length: Optional[int] = None
    max_chain_length: Optional[int] = None
    custom_algorithm_settings: Optional[Dict[str, int]] = None


@dataclass
class OptimizerConfiguration:
    scoring: List[List[Dict[str, int]]]
    limitations: Optional[Limitations] = None


@dataclass
class CompatibilityGraphEntry:
    donor_id: int
    recipient_id: int
    weights: Dict[str, int]


@dataclass
class OptimizerRequest:
    compatibility_graph: List[CompatibilityGraphEntry]
    pairs: List[Pair]
    configuration: OptimizerConfiguration
