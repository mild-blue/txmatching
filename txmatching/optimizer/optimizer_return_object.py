from dataclasses import dataclass
from typing import List


@dataclass
class DonorToRecipient:
    donor_id: int
    recipient_id: int
    score: List[int]


@dataclass
class CycleOrChain:
    patients: List[DonorToRecipient]
    scores: List[int]


@dataclass
class Statistics:
    number_of_found_cycles_and_chains: int
    number_of_found_transplants: int


@dataclass
class OptimizerReturn:
    cycles_and_chains: List[CycleOrChain]
    statistics: Statistics
