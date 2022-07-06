import threading
from typing import Callable, TypeVar

from txmatching.auth.exceptions import SolverAlreadyRunningException

# because these are not constants
# pylint: disable=invalid-name

_solver_running_lock = threading.Lock()
_solver_running = False

T = TypeVar('T')


def run_with_solver_lock(block: Callable[[], T]) -> T:
    """
    Runs execution with the lock, if some other execution is running right now,
    it raises SolverAlreadyRunningException.
    """
    # pylint: disable=global-statement
    # pylint: disable=global-variable-not-assigned
    global _solver_running_lock, _solver_running
    try:
        # check whether another solver is running
        with _solver_running_lock:
            if _solver_running:
                raise SolverAlreadyRunningException()
            _solver_running = True
        # execute block outside of the lock
        return block()
    finally:
        with _solver_running_lock:
            _solver_running = False
