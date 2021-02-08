import mip

from txmatching.solvers.ilp_solver.solution import Status


def val_to_bool(v: float) -> bool:
    return v >= 0.5


def mip_var_to_bool(v: mip.Var) -> bool:
    return val_to_bool(v.x)


def mip_get_result_status(model: mip.Model) -> Status:
    solve_status = model.status

    if solve_status == mip.OptimizationStatus.FEASIBLE:
        return Status.Heuristic
    elif solve_status == mip.OptimizationStatus.OPTIMAL:
        return Status.Optimal
    elif solve_status == mip.OptimizationStatus.INFEASIBLE:
        return Status.Infeasible
    elif solve_status == mip.OptimizationStatus.INT_INFEASIBLE:
        raise NotImplementedError()
    else:
        return Status.NoSolution
