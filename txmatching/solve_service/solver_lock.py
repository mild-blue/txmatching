import threading
from typing import Callable, TypeVar

from txmatching.auth.exceptions import SolverAlreadyRunningException

_solver_running_lock = threading.Lock()
_solver_running = False

T = TypeVar('T')


def run_with_solver_lock(fn: Callable[[], T]) -> T:
    """
    Runs execution with the lock, if some other execution is running right now,
    it raises SolverAlreadyRunningException.
    """
    global _solver_running_lock, _solver_running
    try:
        with _solver_running_lock:
            if _solver_running:
                raise SolverAlreadyRunningException()
            else:
                _solver_running = True

        return fn()
    finally:
        with _solver_running_lock:
            _solver_running = False
