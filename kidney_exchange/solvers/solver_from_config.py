from kidney_exchange.config.configuration import Configuration
from kidney_exchange.solvers.all_solutions_solver import AllSolutionsSolver
from kidney_exchange.solvers.solver_base import SolverBase

_supported_solvers = [AllSolutionsSolver]


def make_solver_from_config(configuration: Configuration) -> SolverBase:
    solver_name_to_solver_constructor = {solver.__name__: solver for solver in _supported_solvers}
    solver_constructor = solver_name_to_solver_constructor.get(configuration.solver_constructor_name)

    if solver_constructor is None:
        raise NotImplementedError(f"Solver {configuration.solver_constructor_name} not supported yet")

    solver = solver_constructor.from_config(configuration)

    return solver


if __name__ == "__main__":
    config = Configuration()
    solver_made_from_config = make_solver_from_config(config)
    print(solver_made_from_config)
