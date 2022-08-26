from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Pair:
    donor_id: int
    recipient_id: Optional[int]


@dataclass
class Limitations:
    max_cycle_length: Optional[int]
    max_chain_length: Optional[int]
    custom_algorithm_settings: Optional[Dict[str, int]]


@dataclass
class OptimizerConfiguration:
    limitations: Optional[Limitations]
    scoring: Optional[List[List[Dict[str, int]]]]


@dataclass
class OptimizerRequest:
    compatibility_graph: List[Dict[str, int]]
    pairs: List[Pair]
    configuration: OptimizerConfiguration
