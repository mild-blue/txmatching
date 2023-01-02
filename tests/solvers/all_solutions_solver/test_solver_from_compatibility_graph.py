import json
import unittest
from typing import Dict, List

import numpy as np

from tests.solvers.tabular_scorer import TabularScorer
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.hla_model import HLAAntibodies, HLATyping
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.solvers.all_solutions_solver.compatibility_graph_solver import \
    find_optimal_paths
from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
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
            find_optimal_paths(compatibility_graph=compatibility_graph,
                               original_donor_idx_to_recipient_idx=donor_idx_to_recipient_idx,
                               donors=_get_donors(len(self._score_matrix)),
                               recipients=_get_recipients(len(self._score_matrix[0])),
                               config_parameters=ConfigParameters(
                                   solver_constructor_name=Solver.AllSolutionsSolver,
                                   max_cycle_length=100,
                                   max_sequence_length=100,
                                   max_number_of_distinct_countries_in_round=100)
                               )
        )
        all_scores = []
        for solution in all_solutions:
            solution_score = sum(
                [scorer.score_transplant_ij(pair.donor_idx, pair.recipient_idx)['hla_compatibility_score']
                 for pair in solution])
            all_scores.append(solution_score)
        self.assertEqual(len(all_solutions[0]), 9)
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

        solutions = find_optimal_paths(compatibility_graph_test,
                                       donor_idx_to_recipient_idx,
                                       _get_donors(len(score_matrix_test)),
                                       _get_recipients(4),
                                       ConfigParameters(
                                           solver_constructor_name=Solver.AllSolutionsSolver,
                                           max_sequence_length=100,
                                           max_cycle_length=100))
        solutions = list(solutions)
        self.assertEqual(4, len(solutions[0]))

    def test_handling_correctly_multiple_donors_with_the_same_recipient(self):
        """
        situation
        D1 __ R1
        D2 _/
        D3 __ R2
        D4 __ R3
        and D3 and D4 can give to r1 and d1 to r2 and d2 to r3
        correct solution are two cycles: only d1 -> r2, d2 -> r1 and d2 -> r3, d3 -> r1. but not both together
        """

        original_donor_idx_to_recipient_idx = {0: 0, 1: 0, 2: 1, 3: 2}

        compatibility_graph_test = {(0, 1): {"hla_compatibility_score": 11}, (1, 2): {"hla_compatibility_score": 10},
                                    (2, 0): {"hla_compatibility_score": 10}, (3, 0): {"hla_compatibility_score": 10}}

        solutions = list(find_optimal_paths(
            compatibility_graph_test,
            original_donor_idx_to_recipient_idx,
            _get_donors(len(original_donor_idx_to_recipient_idx)),
            _get_recipients(3),
            ConfigParameters(
                solver_constructor_name=Solver.AllSolutionsSolver,
                max_sequence_length=100,
                max_cycle_length=100))
        )
        self.assertEqual(len(solutions), 2)
        self.assertCountEqual({pair.recipient_idx for pair in solutions[0]}, {0, 1})
        self.assertCountEqual({pair.recipient_idx for pair in solutions[1]}, {0, 2})

        for solution in solutions:
            recipient_ids = [pair.recipient_idx for pair in solution]

            seen = set()
            duplicates = [x for x in recipient_ids if x in seen or seen.add(x)]

            if duplicates:
                raise Exception(
                    f'Recipient/recipients with id/ids {duplicates} is/are present in a matching more than once')

    def test_handling_correctly_multiple_donors_with_the_same_recipient_at_the_end_of_chain(self):
        """
        situation
        D1 __ R1
        D2 _/
        D4 __ no recipient
        """

        original_donor_idx_to_recipient_idx = {0: 0, 1: 0, 2: -1}

        compatibility_graph_test = {(2, 0): {"hla_compatibility_score": 15}}

        solutions = list(find_optimal_paths(
            compatibility_graph_test,
            original_donor_idx_to_recipient_idx,
            _get_donors(len(original_donor_idx_to_recipient_idx)),
            _get_recipients(1),
            ConfigParameters(
                solver_constructor_name=Solver.AllSolutionsSolver,
                max_sequence_length=100,
                max_cycle_length=100))
        )
        set_of_solutions = []

        # check that solutions are unique
        for sol in solutions:
            self.assertTrue(sol not in set_of_solutions)
            set_of_solutions.append(sol)

        self.assertEqual(len(solutions), 1)

    def test_works_with_one_cycle_only(self):
        """
        This simple case with one sequence has to work and it had initially some issue, so we added this test.
        """

        original_donor_idx_to_recipient_idx = {0: -1, 1: 0}

        compatibility_graph_test = {(0, 0): {'hla_compatibility_score': 0}}

        solutions = list(find_optimal_paths(
            compatibility_graph_test,
            original_donor_idx_to_recipient_idx,
            _get_donors(len(original_donor_idx_to_recipient_idx)),
            _get_recipients(1),
            ConfigParameters(
                solver_constructor_name=Solver.AllSolutionsSolver,
                max_sequence_length=100,
                max_cycle_length=100))
        )
        self.assertEqual([DonorRecipientPairIdxOnly(donor_idx=0, recipient_idx=0)], solutions[0])


def _get_donors(ndonors: int) -> List[Donor]:
    donors = []
    for i in range(ndonors):
        donors.append(Donor(
            parameters=PatientParameters(country_code=Country.CZE,
                                         blood_group=BloodGroup.ZERO,
                                         hla_typing=HLATyping(hla_types_raw_list=[], hla_per_groups=[])
                                         ),
            db_id=i,
            medical_id=f'test_{i}',
            etag=1,
            parsing_issues=[]
        ))
    return donors


def _get_recipients(nrecipients: int) -> List[Recipient]:
    recipients = []
    for i in range(nrecipients):
        recipients.append(Recipient(
            parameters=PatientParameters(country_code=Country.CZE,
                                         blood_group=BloodGroup.ZERO,
                                         hla_typing=HLATyping(hla_types_raw_list=[], hla_per_groups=[])
                                         ),
            db_id=i,
            medical_id=f'test_{i}',
            etag=1,
            parsing_issues=[],
            related_donors_db_ids=[],
            acceptable_blood_groups=[],
            hla_antibodies=HLAAntibodies(hla_antibodies_raw_list=[], hla_antibodies_per_groups=[])
        ))
    return recipients


def _get_compatibility_graph_from_score_matrix(score_matrix: np.array) -> CompatibilityGraph:
    compatibility_graph = {}
    for row_enum, row in enumerate(score_matrix):
        for score_enum, score in enumerate(row):
            if score >= 0:
                compatibility_graph[(row_enum, score_enum)] = {"hla_compatibility_score": score}
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
