from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DonorToRecipient:
    donor_id: int
    recipient_id: int
    weights: Dict[str, int]


@dataclass
class CycleOrChain:
    arcs: List[DonorToRecipient]
    cycle_weights: Dict[str, int]


@dataclass
class Statistics:
    number_of_selected_cycles: int
    number_of_selected_chains: int
    number_of_selected_transplants: int
    final_level: int
    aggregated_weights: Dict[str, int]


@dataclass
class OptimizerReturn:
    selected_cycles_and_chains: List[CycleOrChain]
    statistics: Statistics
