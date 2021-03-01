from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple


class Status(str, Enum):
    NoSolution = 'NoSolution'
    Optimal = 'Optimal'
    Infeasible = 'Infeasible'
    Heuristic = 'Heuristic'


@dataclass
class Solution:
    edges: Iterable[Tuple[int, int]]
