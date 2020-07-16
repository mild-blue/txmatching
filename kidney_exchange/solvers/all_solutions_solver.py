import logging
from typing import List, Tuple, Dict, Iterator, Set

import numpy as np
from graph_tool import topology
from graph_tool.all import Graph

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.additive_scorer import AdditiveScorer, ORIGINAL_DONOR_RECIPIENT_TUPLE
from kidney_exchange.scorers.scorer_base import TRANSPLANT_IMPOSSIBLE
from kidney_exchange.solvers.matching.matching import Matching
from kidney_exchange.solvers.solver_base import SolverBase

logger = logging.getLogger(__name__)


class AllSolutionsSolver(SolverBase):
    # TODO: This is legacy code, refactor, try to optimize speed https://trello.com/c/lKFXAQfE
    def __init__(self, verbose: bool = True):
        super().__init__()
        self._verbose = verbose

    def solve(self, donors: List[Donor], recipients: List[Recipient], scorer: AdditiveScorer) -> Iterator[Matching]:
        score_matrix = scorer.get_score_matrix(donors, recipients)
        score_matrix_array = np.zeros((len(donors), len(recipients)))
        for row_index, row in enumerate(score_matrix):
            for column_index, value in enumerate(row):
                if value == ORIGINAL_DONOR_RECIPIENT_TUPLE:
                    value = np.NaN
                elif value == TRANSPLANT_IMPOSSIBLE:
                    value = - np.inf

                score_matrix_array[row_index, column_index] = value

        for solution in self._solve(score_matrix=score_matrix_array):
            matching = Matching(donor_recipient_list=[(donors[i], recipients[j]) for i, j in solution
                                                      if i < len(donors) and j < len(recipients)])
            yield matching

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
            logger.info("Empty set of paths, returning empty iterator")
            return []

        if self._verbose:
            logger.info(f"Constructing intersection graph, "
                        f"#circuits: {len(pure_circuits)}, #paths: {len(bridge_paths)}")
        intersection_graph, vertex_to_set = self._construct_intersection_graph(all_paths)

        if self._verbose:
            logger.info("Listing all max cliques")

        # TODO: Fix this properly https://trello.com/c/0GBzQWt2
        if len(list(intersection_graph.vertices())) > 0:
            max_cliques = list(topology.max_cliques(intersection_graph))
        else:
            max_cliques = []

        if self._verbose:
            logger.info("Finding 1 vertex cliques")
        used_vertices = set()
        all_vertices = set([intersection_graph.vertex_index[vertex] for vertex in vertex_to_set.keys()])

        for clique in max_cliques:
            used_vertices.update(clique)

        single_vertex_cliques = [[v] for v in all_vertices - used_vertices]
        max_cliques.extend(single_vertex_cliques)

        if self._verbose:
            logger.info("Creating pairings from paths and circuits ")
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
        return list(np.where(np.isfinite(score_matrix[donor_index]))[0])

    def _graph_from_score_matrix(self, score_matrix: np.array,
                                 add_fake_edges_for_bridge_donors: bool = False) -> Tuple[Graph, Dict]:
        n_donors, n_recipients = score_matrix.shape

        recipient_index_to_pair_index = {recipient_ix: donor_ix for donor_ix, recipient_ix in
                                         zip(*np.where(np.isnan(score_matrix)))}

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

        # Add recipient -> bridge donors edges
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
        bridge_indices = np.where(np.sum(np.isnan(score_matrix), axis=1) == 0)[0]
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
        n_donor, n_recipient = score_matrix.shape
        for pair_index in range(n_donor):
            recipient_indices = np.where(np.isnan(score_matrix[pair_index, :]))[0]
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
    def from_config(cls, configuration: Configuration) -> "AllSolutionsSolver":
        return AllSolutionsSolver()


if __name__ == "__main__":
    x = np.array([np.NAN, np.NINF, 0.0, 9.8])
    indices = list(np.where(np.isfinite(x))[0])
    logger.info(indices)

    matrix = np.array([[1, 2, 3], [4, 5, 6]])
    new_matrix_1 = matrix[-1, :]
    logger.info(new_matrix_1)

    logger.info(matrix.shape)

    score_matrix_test = np.array([[np.NAN, np.NINF, 10.2, 13.1],
                                  [0.2, np.NAN, np.NINF, 1],
                                  [0.1, 10.2, 10.3, np.NAN],
                                  [np.NINF, np.NINF, np.NAN, 10],
                                  [0.2, 0.4, np.NINF, 0.5],
                                  [0.2, np.NINF, np.NINF, 0.5]])

    test_solver = AllSolutionsSolver()
    solutions = test_solver._solve(score_matrix_test)
    for test_solution in solutions:
        logger.info(test_solution)
