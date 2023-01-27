from typing import Dict, List, Tuple

from txmatching.optimizer.optimizer_request_object import \
    CompatibilityGraphEntry

CompatibilityGraph = Dict[Tuple[int, int], Dict[str, int]]

OptimizerCompatibilityGraph = List[CompatibilityGraphEntry]
