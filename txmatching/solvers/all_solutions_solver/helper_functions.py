from typing import Dict, Iterable, List, Set, Tuple, Union

import numpy as np
from graph_tool import Graph, topology

from txmatching.scorers.scorer_constants import ORIGINAL_DONOR_RECIPIENT_SCORE
from txmatching.solve_service.data_objects.donor_recipient import \
    DonorIdRecipientIdPair
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair

Path = Tuple[int]


def find_all_circuits(graph: Graph) -> List[Path]:
    """
    Circuits between pairs, each pair is denoted by it's pair = donor index
    """
    return [tuple(circuit) for circuit in topology.all_circuits(graph)]


def find_all_bridge_paths(score_matrix: np.ndarray) -> List[Path]:
    bridge_indices = get_bridge_indices(score_matrix)
    donor_pair_index_to_recipient_pair_indices = get_donor_pair_index_to_recipient_pairs_indices(score_matrix)

    paths = []

    for bridge_index in bridge_indices:
        bridge_paths = find_all_paths_starting_with(bridge_index, donor_pair_index_to_recipient_pair_indices,
                                                    set(bridge_indices))
        paths.extend(bridge_paths)

    paths = [tuple(path) for path in paths if len(path) > 1]
    return paths


def get_pairs_from_clique(clique,
                          path_number_to_path: Dict[int, Path],
                          pure_circuits: List[Path],
                          pair_index_to_recipient_index: Dict[int, int]):
    circuit_list = [path_number_to_path[path_number] for path_number in clique]

    for circuit_index, circuit in enumerate(circuit_list):
        if circuit in pure_circuits:
            circuit_list[circuit_index] = tuple(list(circuit) + [circuit[0]])

    return [DonorIdRecipientIdPair(circuit[i], pair_index_to_recipient_index[circuit[i + 1]])
            for circuit in circuit_list for i in range(len(circuit) - 1)]


def construct_intersection_graph(all_paths: List[Path]) -> Tuple[Graph, Dict[int, Path]]:
    graph = Graph(directed=False)

    path_number_to_path = {path_number: path for path_number, path in enumerate(all_paths)}
    path_to_path_number = {path: path_number for path_number, path in enumerate(all_paths)}

    unique_indices = {index for path in all_paths for index in path}

    index_to_paths_not_having_index = {index: {path for path in all_paths if index not in path} for index in
                                       unique_indices}
    compatible_paths = []
    for path_1 in all_paths:
        item_complementary_set_list = [index_to_paths_not_having_index[item] for item in path_1]
        complementary_paths = set.intersection(*item_complementary_set_list)

        index_1 = path_to_path_number[path_1]
        for path_2 in complementary_paths:
            index_2 = path_to_path_number[path_2]
            compatible_paths.append((index_1, index_2))

    graph.add_edge_list(compatible_paths)
    return graph, path_number_to_path


def find_acceptable_recipient_indices(score_matrix: np.ndarray, donor_index: int) -> List[int]:
    return list(np.where((score_matrix[donor_index] >= 0))[0])


def graph_from_score_matrix(score_matrix: np.array,
                            add_fake_edges_for_bridge_donors: bool = False) -> Tuple[Graph, Dict]:
    n_donors, _ = score_matrix.shape

    recipient_index_to_pair_index = {recipient_ix: donor_ix for donor_ix, recipient_ix in
                                     zip(*np.where(score_matrix == ORIGINAL_DONOR_RECIPIENT_SCORE))}

    directed_graph = Graph(directed=True)
    pair_index_to_vertex = {i: directed_graph.add_vertex() for i in range(n_donors)}

    # Add donor -> recipient edges
    for pair_index in range(n_donors):
        source_vertex = pair_index_to_vertex[pair_index]
        recipient_indices = find_acceptable_recipient_indices(score_matrix, pair_index)

        if len(recipient_indices) == 0:
            continue

        for recipient_index in recipient_indices:
            target_pair_index = recipient_index_to_pair_index[recipient_index]
            target_vertex = pair_index_to_vertex[target_pair_index]

            directed_graph.add_edge(source_vertex, target_vertex)

    # Add recipient -> bridge donors edges, done differently now, not used anymore
    if add_fake_edges_for_bridge_donors:
        bridge_indices = get_bridge_indices(score_matrix)
        regular_indices = [i for i in range(n_donors) if i not in bridge_indices]
        for bridge_index in bridge_indices:
            bridge_vertex = pair_index_to_vertex[bridge_index]
            for regular_index in regular_indices:
                regular_vertex = pair_index_to_vertex[regular_index]
                directed_graph.add_edge(regular_vertex, bridge_vertex)

    # add_names_to_vertices(directed_graph, pair_index_to_vertex)

    return directed_graph, pair_index_to_vertex


def get_bridge_indices(score_matrix: np.ndarray) -> List[int]:
    bridge_indices = np.where(np.sum(score_matrix == ORIGINAL_DONOR_RECIPIENT_SCORE, axis=1) == 0)[0]
    return list(bridge_indices)


def get_donor_pair_index_to_recipient_pairs_indices(score_matrix: np.ndarray) -> Dict[int, List[int]]:
    n_donors, _ = score_matrix.shape

    donor_index_to_recipient_indices = {
        donor_index: find_acceptable_recipient_indices(score_matrix, donor_index)
        for donor_index in range(n_donors)}

    pair_index_to_recipient_index = construct_pair_index_to_recipient_index(score_matrix)
    recipient_index_to_pair_index = {recipient_index: pair_index for pair_index, recipient_index
                                     in pair_index_to_recipient_index.items()}

    donor_pair_index_to_recipient_pair_indices = {
        donor_index: [recipient_index_to_pair_index[recipient_index] for recipient_index in recipient_indices]
        for donor_index, recipient_indices in donor_index_to_recipient_indices.items()}

    return donor_pair_index_to_recipient_pair_indices


def construct_pair_index_to_recipient_index(score_matrix: np.ndarray) -> Dict[int, int]:
    pair_index_to_recipient_index = dict()
    n_donor, _ = score_matrix.shape
    for pair_index in range(n_donor):
        recipient_indices = np.where(score_matrix[pair_index, :] == ORIGINAL_DONOR_RECIPIENT_SCORE)[0]
        if len(recipient_indices) > 0:
            pair_index_to_recipient_index[pair_index] = recipient_indices[0]

    return pair_index_to_recipient_index


def find_all_paths_starting_with(source: int, source_to_targets: Dict[int, List[int]],
                                 covered_indices: Set) -> List[List[int]]:
    targets = source_to_targets[source]
    remaining_targets = set(targets) - covered_indices

    paths = [[source]]

    for target in remaining_targets:
        covered_indices.add(target)
        paths_starting_with_target = find_all_paths_starting_with(target, source_to_targets, covered_indices)
        covered_indices.remove(target)

        for path in paths_starting_with_target:
            path.insert(0, source)
        paths.extend(paths_starting_with_target)

    return paths


def get_score_for_pairs(score_matrix_array: np.array,
                        pairs: Iterable[Union[DonorIdRecipientIdPair, DonorRecipientPair]]):
    pairs = list(pairs)
    if isinstance(pairs[0], DonorIdRecipientIdPair):
        return sum([score_matrix_array[pair.donor, pair.recipient] for pair in pairs])
    if isinstance(pairs[0], DonorRecipientPair):
        return sum([score_matrix_array[pair.donor.db_id, pair.recipient.db_id] for pair in pairs])
    raise TypeError('Unexpected type to score')
