from dataclasses import dataclass

from txmatching.solvers.ilp_solver.solution import Solution, Status


@dataclass
class Result:
    status: Status
    solution: Solution = None
