import json
import unittest
from typing import Dict, List

import numpy as np

from tests.solvers.tabular_scorer import TabularScorer
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.hla_model import HLATyping
from txmatching.patients.patient import Donor
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.solvers.all_solutions_solver.compatibility_graph_solver import \
    find_possible_path_combinations_from_compatibility_graph
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Solver
from txmatching.utils.get_absolute_path import get_absolute_path


class TestAllSolutionsSolver(unittest.TestCase):
    def setUp(self) -> None:
        sample_score_matrix_path = get_absolute_path('/tests/resources/sample_score_matrix.json')
        with open(sample_score_matrix_path, 'r') as sample_score_matrix_file:
            self._score_matrix = json.load(sample_score_matrix_file)

        self._expected_max_score = 92.0
        self._expected_num_solutions = 1766

    def test_solve(self):
        # TODO: Add more specific test https://trello.com/c/1Cdaujkx
        compatibility_graph = _get_compatibility_graph_from_score_matrix(self._score_matrix)
        scorer = TabularScorer(compatibility_graph=compatibility_graph)
        donor_idx_to_recipient_idx = _get_donor_idx_to_recipient_idx_from_score_matrix(self._score_matrix)
        all_solutions = list(
            find_possible_path_combinations_from_compatibility_graph(compatibility_graph=compatibility_graph,
                                                                     donor_idx_to_recipient_idx=donor_idx_to_recipient_idx,
                                                                     donors=_get_donors_for_score_matrix(
                                                                         self._score_matrix),
                                                                     config_parameters=ConfigParameters(
                                                                         solver_constructor_name=Solver.AllSolutionsSolver,
                                                                         max_cycle_length=100,
                                                                         max_sequence_length=100,
                                                                         max_number_of_distinct_countries_in_round=100)
                                                                     )
        )
        all_scores = []
        for solution in all_solutions:
            solution_score = sum([scorer.score_transplant_ij(pair.donor_idx, pair.recipient_idx)
                                  for pair in solution])
            all_scores.append(solution_score)

        self.assertEqual(self._expected_num_solutions, len(all_solutions))
        self.assertEqual(self._expected_max_score, max(all_scores))

    def test_solve_specific(self):
        score_matrix_test = np.array([[-2.0, -1.0, 10.2, 13.1],
                                      [0.2, -2.0, -1.0, 1],
                                      [0.1, 10.2, 10.3, -2.0],
                                      [-1.0, -1.0, -2.0, 10],
                                      [0.2, 0.4, -1.0, 0.5],
                                      [0.2, -1.0, -1.0, 0.5]])

        compatibility_graph_test = _get_compatibility_graph_from_score_matrix(score_matrix_test)
        donor_idx_to_recipient_idx = _get_donor_idx_to_recipient_idx_from_score_matrix(score_matrix_test)

        solutions = find_possible_path_combinations_from_compatibility_graph(compatibility_graph_test,
                                                                             donor_idx_to_recipient_idx,
                                                                             _get_donors_for_score_matrix(
                                                                                 score_matrix_test),
                                                                             ConfigParameters(
                                                                                 solver_constructor_name=Solver.AllSolutionsSolver,
                                                                                 max_sequence_length=100,
                                                                                 max_cycle_length=100))
        self.assertEqual(36, len(list(solutions)))


def _get_donors_for_score_matrix(score_matrix: np.array) -> List[Donor]:
    donors = []
    for _ in range(len(score_matrix)):
        donors.append(Donor(
            parameters=PatientParameters(country_code=Country.CZE,
                                         blood_group=BloodGroup.ZERO,
                                         hla_typing=HLATyping(hla_types_raw_list=[], hla_per_groups=[])
                                         ),
            db_id=1,
            medical_id='test',
            etag=1,
            parsing_issues=[]
        ))
    return donors


def _get_compatibility_graph_from_score_matrix(score_matrix: np.array) -> CompatibilityGraph:
    compatibility_graph = {}
    for row_enum, row in enumerate(score_matrix):
        for score_enum, score in enumerate(row):
            if score >= 0:
                compatibility_graph[(row_enum, score_enum)] = score
    return compatibility_graph


def _get_donor_idx_to_recipient_idx_from_score_matrix(score_matrix: np.array) -> Dict[int, int]:
    donor_idx_to_recipient_idx = {}
    for donor_enum, row in enumerate(score_matrix):
        for recipient_enum, score in enumerate(row):
            if score == -2:
                donor_idx_to_recipient_idx[donor_enum] = recipient_enum

    for donor_enum, row in enumerate(score_matrix):
        if donor_enum not in donor_idx_to_recipient_idx:
            donor_idx_to_recipient_idx[donor_enum] = -1

    return donor_idx_to_recipient_idx
