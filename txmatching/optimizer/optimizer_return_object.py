from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DonorToRecipient:
    donor_id: int
    recipient_id: int
    score: List[int]


@dataclass
class Statictics:
    number_of_found_cycles: int
    number_of_found_transplants: int


@dataclass
class OptimizerReturn:
    cycles_and_chains: List[Optional[List[DonorToRecipient]]]
    statistics: Statictics
