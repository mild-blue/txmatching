# pylint: skip-file
# at the moment the solver is not optimal but works alright. We do not want to invest time in its improvement
# at the moment as later there might be some complete rewrite of it if it bothers us.
import logging
from typing import Dict, Iterator, List, Set, Tuple

import numpy as np
from graph_tool import topology
from graph_tool.all import Graph

from txmatching.config.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import RecipientDbId, DonorDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.scorer_constants import ORIGINAL_DONOR_RECIPIENT_SCORE
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


class AllSolutionsSolver(SolverBase):
    # TODO: This is legacy code, refactor, try to optimize speed https://trello.com/c/lKFXAQfE
    def __init__(self, max_number_of_distinct_countries_in_round: int, verbose: bool = True):
        super().__init__()
        self._verbose = verbose
        self._max_number_of_distinct_countries_in_round = max_number_of_distinct_countries_in_round

    def solve(self, donors_dict: Dict[DonorDbId, Donor],
              recipients_dict: Dict[RecipientDbId, Recipient], scorer: AdditiveScorer) -> Iterator[MatchingWithScore]:
        score_matrix = scorer.get_score_matrix(donors_dict, recipients_dict)
        recipients = list(recipients_dict.values())
        donors = list(donors_dict.values())
        score_matrix_array = np.zeros((len(donors), len(recipients)))
        for row_index, row in enumerate(score_matrix):
            for column_index, value in enumerate(row):
                score_matrix_array[row_index, column_index] = value
        proper_solutions = set()

        db_id = 0
        for solution in self._solve(score_matrix=score_matrix_array):
            db_id += 1
            donor_recipient_list = [(donors[i], recipients[j]) for i, j in solution
                                    if i < len(donors) and j < len(recipients)]
            score = sum([score_matrix_array[i, j] for i, j in solution
                         if i < len(donors) and j < len(recipients)])

            matching = MatchingWithScore(donor_recipient_list, score, db_id)
            if max([transplant_round.country_count for transplant_round in
                    matching.get_rounds()]) <= self._max_number_of_distinct_countries_in_round:
                yield matching
                proper_solutions.add(matching)
            else:
                proper_rounds = [transplant_round for transplant_round in
                                 matching.get_rounds() if
                                 transplant_round.country_count <= self._max_number_of_distinct_countries_in_round]
                if len(proper_rounds) > 0:
                    donor_recipient_list = [donor_recipient for transplant_round in proper_rounds for donor_recipient in
                                            transplant_round.donor_recipient_list]
                    score = sum(
                        [score_matrix_array[donors.index(donor), recipients.index(recipient)] for
                         donor, recipient in
                         donor_recipient_list])
                    proper_matching = MatchingWithScore(donor_recipient_list, score, db_id)
                    if proper_matching not in proper_solutions:
                        yield proper_matching
                        proper_solutions.add(proper_matching)

    def _solve(self, score_matrix: np.ndarray) -> Iterator[List[Tuple[int, int]]]:
        """
        Returns iterator over the optimal matching. The result is a list of pairs. Each pair consists of two integers
        which correspond to recipient, donor indices in the self._donors, resp. self._recipients lists.

        :param score_matrix: matrix of Score(i,j) for transplant from donor_i to recipient_j
            special values are:
            UNACCEPTABLE_SCORE = np.NINF
            DEFAULT_DONOR_RECIPIENT_PAIR_SCORE = np.NAN
        """
        graph, _ = self._graph_from_score_matrix(score_matrix)
        pure_circuits = [tuple(circuit) for circuit in self._find_all_circuits(graph)]
        bridge_paths = self._find_all_bridge_paths(score_matrix)

        all_paths = pure_circuits + bridge_paths

        if len(all_paths) == 0:
            logger.info('Empty set of paths, returning empty iterator')
            return []

        if self._verbose:
            logger.info(f'Constructing intersection graph, '
                        f'#circuits: {len(pure_circuits)}, #paths: {len(bridge_paths)}')
        intersection_graph, vertex_to_set = self._construct_intersection_graph(all_paths)

        if self._verbose:
            logger.info('Listing all max cliques')

        # TODO: Fix this properly https://trello.com/c/0GBzQWt2
        if len(list(intersection_graph.vertices())) > 0:
            max_cliques = list(topology.max_cliques(intersection_graph))
        else:
            max_cliques = []

        if self._verbose:
            logger.info('Finding 1 vertex cliques')
        used_vertices = set()
        all_vertices = {intersection_graph.vertex_index[vertex] for vertex in vertex_to_set.keys()}

        for clique in max_cliques:
            used_vertices.update(clique)

        single_vertex_cliques = [[v] for v in all_vertices - used_vertices]
        max_cliques.extend(single_vertex_cliques)

        if self._verbose:
            logger.info('Creating pairings from paths and circuits ')
        pair_index_to_recipient_index = self._construct_pair_index_to_recipient_index(score_matrix)

        for clique in max_cliques:
            circuit_list = [vertex_to_set[v] for v in clique]

            for circuit_index, circuit in enumerate(circuit_list):
                if circuit in pure_circuits:
                    circuit_list[circuit_index] = tuple(list(circuit) + [circuit[0]])

            pairs = [[(circuit[i], pair_index_to_recipient_index[circuit[i + 1]])
                      for i in range(len(circuit) - 1)]
                     for circuit in circuit_list]
            pairs = [pair for pair_sublist in pairs for pair in pair_sublist]
            yield pairs

    @staticmethod
    def _construct_intersection_graph(sets: List[Tuple[int]]) -> Tuple[Graph, Dict[int, Tuple[int]]]:
        graph = Graph(directed=False)

        i_to_set = {index: st for index, st in enumerate(sets)}

        unique_indices = set()
        for st in sets:
            unique_indices.update(st)

        index_to_sets_not_having_index = {i: {st for st in sets if i not in st} for i in unique_indices}

        set_to_index = {st: index for index, st in enumerate(sets)}
        n_sets = len(sets)
        adjacency_matrix = np.zeros((n_sets, n_sets))

        for set_1 in sets:
            item_complementary_set_list = [index_to_sets_not_having_index[item] for item in set_1]
            complementary_sets = set.intersection(*item_complementary_set_list)

            index_1 = set_to_index[set_1]
            for set_2 in complementary_sets:
                index_2 = set_to_index[set_2]
                adjacency_matrix[index_1, index_2] = True

        graph.add_edge_list(np.transpose(adjacency_matrix.nonzero()))
        return graph, i_to_set

    @staticmethod
    def _find_all_circuits(graph: Graph) -> Iterator[List[int]]:
        """
        Circuits between pairs, each pair is denoted by it's pair = donor index
        """
        for circuit in topology.all_circuits(graph):
            yield list(circuit)

    @staticmethod
    def _find_acceptable_recipient_indices(score_matrix: np.ndarray, donor_index: int) -> List[int]:
        return list(np.where((score_matrix[donor_index] >= 0))[0])

    def _graph_from_score_matrix(self, score_matrix: np.array,
                                 add_fake_edges_for_bridge_donors: bool = False) -> Tuple[Graph, Dict]:
        n_donors, _ = score_matrix.shape

        recipient_index_to_pair_index = {recipient_ix: donor_ix for donor_ix, recipient_ix in
                                         zip(*np.where(score_matrix == ORIGINAL_DONOR_RECIPIENT_SCORE))}

        directed_graph = Graph(directed=True)
        pair_index_to_vertex = {i: directed_graph.add_vertex() for i in range(n_donors)}

        # Add donor -> recipient edges
        for pair_index in range(n_donors):
            source_vertex = pair_index_to_vertex[pair_index]
            recipient_indices = self._find_acceptable_recipient_indices(score_matrix, pair_index)

            if len(recipient_indices) == 0:
                continue

            for recipient_index in recipient_indices:
                target_pair_index = recipient_index_to_pair_index[recipient_index]
                target_vertex = pair_index_to_vertex[target_pair_index]

                directed_graph.add_edge(source_vertex, target_vertex)

        # Add recipient -> bridge donors edges, done differently now, not used anymore
        if add_fake_edges_for_bridge_donors:
            bridge_indices = self._get_bridge_indices(score_matrix)
            regular_indices = [i for i in range(n_donors) if i not in bridge_indices]
            for bridge_index in bridge_indices:
                bridge_vertex = pair_index_to_vertex[bridge_index]
                for regular_index in regular_indices:
                    regular_vertex = pair_index_to_vertex[regular_index]
                    directed_graph.add_edge(regular_vertex, bridge_vertex)

        # self._add_names_to_vertices(directed_graph, pair_index_to_vertex)

        return directed_graph, pair_index_to_vertex

    def _find_all_bridge_paths(self, score_matrix: np.ndarray) -> List[Tuple[int]]:
        bridge_indices = self._get_bridge_indices(score_matrix)
        donor_pair_index_to_recipient_pair_indices = self._get_donor_pair_index_to_recipient_pairs_indices(score_matrix)

        paths = []

        for bridge_index in bridge_indices:
            bridge_paths = self._find_all_paths_starting_with(bridge_index, donor_pair_index_to_recipient_pair_indices,
                                                              set(bridge_indices))
            paths.extend(bridge_paths)

        paths = [tuple(path) for path in paths if len(path) > 1]
        return paths

    @staticmethod
    def _get_bridge_indices(score_matrix: np.ndarray) -> List[int]:
        bridge_indices = np.where(np.sum(score_matrix == ORIGINAL_DONOR_RECIPIENT_SCORE, axis=1) == 0)[0]
        return list(bridge_indices)

    def _get_donor_pair_index_to_recipient_pairs_indices(self, score_matrix: np.ndarray) -> Dict[int, List[int]]:
        n_donors, _ = score_matrix.shape

        donor_index_to_recipient_indices = {
            donor_index: self._find_acceptable_recipient_indices(score_matrix, donor_index)
            for donor_index in range(n_donors)}

        pair_index_to_recipient_index = self._construct_pair_index_to_recipient_index(score_matrix)
        recipient_index_to_pair_index = {recipient_index: pair_index for pair_index, recipient_index
                                         in pair_index_to_recipient_index.items()}

        donor_pair_index_to_recipient_pair_indices = {
            donor_index: [recipient_index_to_pair_index[recipient_index] for recipient_index in recipient_indices]
            for donor_index, recipient_indices in donor_index_to_recipient_indices.items()}

        return donor_pair_index_to_recipient_pair_indices

    @staticmethod
    def _construct_pair_index_to_recipient_index(score_matrix: np.ndarray) -> Dict[int, int]:
        pair_index_to_recipient_index = dict()
        n_donor, _ = score_matrix.shape
        for pair_index in range(n_donor):
            recipient_indices = np.where(score_matrix[pair_index, :] == ORIGINAL_DONOR_RECIPIENT_SCORE)[0]
            if len(recipient_indices) > 0:
                pair_index_to_recipient_index[pair_index] = recipient_indices[0]

        return pair_index_to_recipient_index

    def _find_all_paths_starting_with(self, source: int, source_to_targets: Dict[int, List[int]],
                                      covered_indices: Set) -> \
            List[List[int]]:
        targets = source_to_targets[source]
        remaining_targets = set(targets) - covered_indices

        paths = [[source]]

        for target in remaining_targets:
            covered_indices.add(target)
            paths_starting_with_target = self._find_all_paths_starting_with(target, source_to_targets, covered_indices)
            covered_indices.remove(target)

            for path in paths_starting_with_target:
                path.insert(0, source)
            paths.extend(paths_starting_with_target)

        return paths

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'AllSolutionsSolver':
        return AllSolutionsSolver(configuration.max_number_of_distinct_countries_in_round)
