from dataclasses import dataclass

from txmatching.solvers.ilp_solver.solution import Solution, Status

# this is not used anywhere, do I keep it for future possibilities or not
@dataclass
class Result:
    status: Status
    solution: Solution = None
