from itertools import groupby
from typing import Dict, List, Set, Tuple

import numpy as np
from graph_tool import Graph, topology

from txmatching.scorers.scorer_constants import ORIGINAL_DONOR_RECIPIENT_SCORE
from txmatching.solvers.all_solutions_solver.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.all_solutions_solver.scoring_utils import \
    get_score_for_idx_pairs

Path = Tuple[int]


def get_donor_idx_to_recipient_idx(score_matrix: np.ndarray) -> Dict[int, int]:
    donor_idx_to_recipient_idx = dict()
    n_donor, _ = score_matrix.shape
    for donor_idx in range(n_donor):
        recipient_indices = np.where(score_matrix[donor_idx, :] == ORIGINAL_DONOR_RECIPIENT_SCORE)[0]
        assert len(recipient_indices) in {0, 1}
        if len(recipient_indices) == 1:
            donor_idx_to_recipient_idx[donor_idx] = recipient_indices[0]

    return donor_idx_to_recipient_idx


def get_compatible_donor_idxs_per_donor_idx(score_matrix: np.ndarray,
                                            donor_idx_to_recipient_idx: Dict[int, int]) -> Dict[int, List[int]]:
    n_donors, _ = score_matrix.shape

    recipient_idx_to_donor_idx = {recipient_idx: donor_idx for donor_idx, recipient_idx
                                  in donor_idx_to_recipient_idx.items()}

    donor_idx_to_recipient_idxs = {
        donor_idx: _find_acceptable_recipient_indices(score_matrix, donor_idx)
        for donor_idx in range(n_donors)}

    compatible_donor_idxs_per_donor_idx = {
        donor_idx: [recipient_idx_to_donor_idx[recipient_index] for recipient_index in recipient_idxs]
        for donor_idx, recipient_idxs in donor_idx_to_recipient_idxs.items()}

    return compatible_donor_idxs_per_donor_idx


def find_all_cycles(n_donors: int,
                    compatible_donor_idxs_per_donor_idx: Dict[int, List[int]],
                    max_length: int) -> List[Path]:
    """
    Circuits between pairs, each pair is denoted by it's pair = donor index
    """
    donor_to_compatible_donor_graph = _get_donor_to_compatible_donor_graph(n_donors,
                                                                           compatible_donor_idxs_per_donor_idx)
    all_circuits = []
    for circuit in topology.all_circuits(donor_to_compatible_donor_graph):
        if len(circuit) <= max_length:
            circuit_with_end = tuple(list(circuit) + [circuit[0]])
            all_circuits.append(circuit_with_end)

    return all_circuits


def find_all_sequences(score_matrix: np.ndarray,
                       compatible_donor_idxs_per_donor_idx: Dict[int, List[int]],
                       max_length: int) -> List[Path]:
    bridge_indices = _get_bridge_indices(score_matrix)

    paths = []

    for bridge_index in bridge_indices:
        bridge_paths = _find_all_paths_starting_with(bridge_index, compatible_donor_idxs_per_donor_idx,
                                                     set(bridge_indices))
        paths.extend(bridge_paths)

    paths = [tuple(path) for path in paths if 1 < len(path) <= max_length]

    return paths


def keep_only_highest_scoring_paths(paths: List[Path],
                                    score_matrix: np.ndarray,
                                    donor_idx_to_recipient_idx: Dict[int, int]) -> List[Path]:
    paths_grouped = [list(group) for _, group in groupby(sorted(paths, key=frozenset), frozenset)]

    paths_filtered = [
        max(path_group,
            key=lambda path: _get_path_score(score_matrix, path, donor_idx_to_recipient_idx))
        for path_group in paths_grouped]

    return paths_filtered


def _get_path_score(score_matrix: np.array,
                    path: Path,
                    donor_idx_to_recipient_idx: Dict[int, int]) -> int:
    pairs = _get_pairs_from_paths([path], donor_idx_to_recipient_idx)
    return get_score_for_idx_pairs(score_matrix, pairs)


def get_pairs_from_clique(clique,
                          path_number_to_path: Dict[int, Path],
                          donor_idx_to_recipient_idx: Dict[int, int]) -> List[DonorRecipientPairIdxOnly]:
    circuit_list = [path_number_to_path[path_number] for path_number in clique]

    return _get_pairs_from_paths(circuit_list, donor_idx_to_recipient_idx)


def _get_pairs_from_paths(paths: List[Tuple[int]],
                          pair_index_to_recipient_index: Dict[int, int]) -> List[DonorRecipientPairIdxOnly]:
    return [DonorRecipientPairIdxOnly(path[i], pair_index_to_recipient_index[path[i + 1]])
            for path in paths for i in range(len(path) - 1)]


# pylint: disable=too-many-locals
# I think here the local variables help the code
def construct_path_intersection_graph(all_paths: List[Path]) -> Tuple[Graph, Dict[int, Path]]:
    graph = Graph(directed=False)

    path_number_to_path = {path_number: path for path_number, path in enumerate(all_paths)}
    path_to_path_number = {path: path_number for path_number, path in enumerate(all_paths)}

    unique_indices = {index for path in all_paths for index in path}

    index_to_path_number_not_having_index = {
        index: {path_to_path_number[path] for path in all_paths if index not in path} for index in
        unique_indices}
    compatible_paths = []
    for path_number, path in enumerate(all_paths):
        complementary_paths_per_item = [index_to_path_number_not_having_index[item] for item in path]
        complementary_path_numbers = set.intersection(*complementary_paths_per_item)

        for complementary_path_number in complementary_path_numbers:
            if complementary_path_number > path_number:
                compatible_paths.append((path_number, complementary_path_number))

    graph.add_edge_list(compatible_paths)
    return graph, path_number_to_path
# pylint: enable=too-many-locals


def _find_acceptable_recipient_indices(score_matrix: np.ndarray, donor_index: int) -> List[int]:
    return list(np.where((score_matrix[donor_index] >= 0))[0])


def _get_donor_to_compatible_donor_graph(n_donors: int,
                                         compatible_donor_idxs_per_donor_idx: Dict[int, List[int]]) -> Graph:
    donor_to_compatible_donor_graph = Graph(directed=True)
    for i in range(n_donors):
        assert i == donor_to_compatible_donor_graph.add_vertex()

    # Add donor -> compatible_donor edges
    for donor_idx, compatible_donor_idxs in compatible_donor_idxs_per_donor_idx.items():

        for compatible_donor_idx in compatible_donor_idxs:
            donor_to_compatible_donor_graph.add_edge(donor_idx, compatible_donor_idx)

    return donor_to_compatible_donor_graph


def _get_bridge_indices(score_matrix: np.ndarray) -> List[int]:
    bridge_indices = np.where(np.sum(score_matrix == ORIGINAL_DONOR_RECIPIENT_SCORE, axis=1) == 0)[0]
    return list(bridge_indices)


def _find_all_paths_starting_with(source: int, source_to_targets: Dict[int, List[int]],
                                  covered_indices: Set) -> List[List[int]]:
    targets = source_to_targets[source]
    remaining_targets = set(targets) - covered_indices

    paths = [[source]]

    for target in remaining_targets:
        covered_indices.add(target)
        paths_starting_with_target = _find_all_paths_starting_with(target, source_to_targets, covered_indices)
        covered_indices.remove(target)

        for path in paths_starting_with_target:
            path.insert(0, source)
        paths.extend(paths_starting_with_target)

    return paths
