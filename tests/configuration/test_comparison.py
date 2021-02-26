import unittest

from txmatching.configuration.configuration import Configuration


class TestComparisonConfiguration(unittest.TestCase):
    def test_comparable(self):
        self.assertTrue(Configuration().comparable(Configuration()))
        self.assertTrue(Configuration(max_matchings_in_all_solutions_solver=10).comparable(
            Configuration(max_matchings_in_all_solutions_solver=100)))
        self.assertFalse(Configuration(max_matchings_in_all_solutions_solver=100).comparable(
            Configuration(max_matchings_in_all_solutions_solver=10)))
        self.assertTrue(
            Configuration(required_patient_db_ids=[2, 1]).comparable(Configuration(required_patient_db_ids=[1, 2])))
        self.assertFalse(
            Configuration(required_patient_db_ids=[1]).comparable(Configuration(required_patient_db_ids=[1, 2])))
