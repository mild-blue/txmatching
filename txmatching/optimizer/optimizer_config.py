from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Limitations:
    max_cycle_length: Optional[int]
    max_chain_length: Optional[int]
    custom_algorithm_settings: Optional[Dict[str, int]]


@dataclass
class OptimizerConfig:
    limitations: Limitations
    scoring: List[List[Dict[str, int]]]
