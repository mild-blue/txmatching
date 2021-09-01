import mip

from txmatching.solvers.ilp_solver.solution import Status


def mip_var_to_bool(var: mip.Var) -> bool:
    maybe_value = var.x
    if maybe_value is None:
        return False
    return maybe_value.real >= 0.5


def mip_get_result_status(model: mip.Model) -> Status:
    solve_status = model.status

    if solve_status == mip.OptimizationStatus.FEASIBLE:
        return Status.HEURISTIC
    elif solve_status == mip.OptimizationStatus.OPTIMAL:
        return Status.OPTIMAL
    elif solve_status == mip.OptimizationStatus.INFEASIBLE:
        return Status.INFEASIBLE
    elif solve_status == mip.OptimizationStatus.INT_INFEASIBLE:
        raise NotImplementedError()
    else:
        return Status.NO_SOLUTION
