import unittest

from kidney_exchange.solvers.solve_from_config import solve_from_db
from kidney_exchange.web import create_app


class TestSolveFromDbAndItsSupportFunctionality(unittest.TestCase):
    def test_caching_in_solve_from_db(self):
        app = create_app()
        with app.app_context():
            self.assertEqual(1, len(solve_from_db()))
