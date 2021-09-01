from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple


class Status(str, Enum):
    NO_SOLUTION = 'NoSolution'
    OPTIMAL = 'Optimal'
    INFEASIBLE = 'Infeasible'
    HEURISTIC = 'Heuristic'


@dataclass
class Solution:
    edges: Iterable[Tuple[int, int]]
