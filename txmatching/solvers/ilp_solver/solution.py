from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, Tuple


class Status(IntEnum):
    NoSolution = 0
    Optimal = 1
    Infeasible = 2
    Heuristic = 3

@dataclass
class Solution:
    edges: Iterable[Tuple[int, int]]
