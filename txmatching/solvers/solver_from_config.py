from txmatching.config.configuration import Configuration
from txmatching.solvers.all_solutions_solver import AllSolutionsSolver
from txmatching.solvers.solver_base import SolverBase
from txmatching.utils.construct_configurable_object import construct_configurable_object

_supported_solvers = [AllSolutionsSolver]


def solver_from_config(config: Configuration) -> SolverBase:
    return construct_configurable_object(config.solver_constructor_name, _supported_solvers, config)
