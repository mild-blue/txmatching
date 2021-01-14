import threading
import time
from unittest import TestCase, mock

from txmatching.auth.exceptions import SolverAlreadyRunningException
from txmatching.solve_service.solver_lock import run_with_solver_lock


class TestSolverLock(TestCase):
    def test_solver_lock_should_work(self):
        model = mock.MagicMock()
        model.run = False

        def test(model):
            model.run = True
            return 'hello'

        self.assertEqual('hello', run_with_solver_lock(lambda: test(model)))
        self.assertEqual(True, model.run)

    def test_solver_lock_should_throw_exception(self):
        model = mock.MagicMock()
        model.run_times = 0

        def test(model, sleep_time):
            time.sleep(sleep_time)
            model.run_times += 1

        thread = threading.Thread(target=lambda: run_with_solver_lock(lambda: test(model, 1)), args=[])
        thread.start()

        self.assertRaises(SolverAlreadyRunningException, lambda: run_with_solver_lock(lambda: test(model, 0)))

        thread.join()
        self.assertEqual(1, model.run_times)
