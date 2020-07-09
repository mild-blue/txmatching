from kidney_exchange.config.configuration import Configuration
from kidney_exchange.solvers.all_solutions_solver import AllSolutionsSolver
from kidney_exchange.solvers.solver_base import SolverBase
from kidney_exchange.utils.construct_configurable_object import construct_configurable_object

_supported_solvers = [AllSolutionsSolver]


def solver_from_config(config: Configuration) -> SolverBase:
    return construct_configurable_object(config.solver_constructor_name, _supported_solvers, config)
