import logging
import tempfile
from os import close, dup, dup2

import mip

from txmatching.solvers.ilp_solver.solution import Status

logger = logging.getLogger(__name__)


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


def solve_with_logging(ilp_model: mip.Model):
    with tempfile.TemporaryFile() as tmp_output:
        orig_std_out = dup(1)
        dup2(tmp_output.fileno(), 1)
        ilp_model.optimize()
        dup2(orig_std_out, 1)
        close(orig_std_out)
        if logging.DEBUG >= logging.root.level:
            tmp_output.seek(0)
            for line in tmp_output.read().splitlines():
                logger.debug(line.decode('utf8'))
