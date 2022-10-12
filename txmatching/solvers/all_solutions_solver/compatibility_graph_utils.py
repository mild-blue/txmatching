import dataclasses
import logging
from itertools import groupby
from typing import Dict, List, Set, Tuple

from graph_tool import Graph, topology

from txmatching.auth.exceptions import TooComplicatedDataForAllSolutionsSolver
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.solvers.all_solutions_solver.scoring_utils import \
    get_score_for_idx_pairs
from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country

Path = Tuple[int]


@dataclasses.dataclass
class PathWithScore:
    donor_ids: Path
    score: int
    debt_per_country: Dict[Country, int]
    debt_blood_zero_per_country: Dict[Country, int]
    length: int


logger = logging.getLogger(__name__)


def get_compatible_donor_idxs_per_donor_idx(compatibility_graph: CompatibilityGraph,
                                            original_donor_idx_to_recipient_idx: Dict[int, int]) -> Dict[
    int, List[int]]:
    donor_idxs = set(original_donor_idx_to_recipient_idx.keys())
    recipient_idxs = set(original_donor_idx_to_recipient_idx.values())

    original_recipient_idx_to_donor_idxs = {
        recipient_idx: [donor_idx for donor_idx, donor_recipient_idx in original_donor_idx_to_recipient_idx.items() if
                        donor_recipient_idx == recipient_idx] for recipient_idx in recipient_idxs}

    donor_idx_to_recipient_idxs = {
        donor_idx: _find_acceptable_recipient_idxs(compatibility_graph, donor_idx)
        for donor_idx in donor_idxs}

    compatible_donor_idxs_per_donor_idx = {
        donor_idx: [dx for list_dx in
                    [original_recipient_idx_to_donor_idxs[recipient_index] for recipient_index in recipient_idxs] for dx
                    in list_dx]
        for donor_idx, recipient_idxs in donor_idx_to_recipient_idxs.items()}

    return compatible_donor_idxs_per_donor_idx


def find_all_cycles(n_donors: int,
                    compatible_donor_idxs_per_donor_idx: Dict[int, List[int]],
                    donors: List[Donor],
                    config_parameters: ConfigParameters,
                    original_donor_idx_to_recipient_idx: Dict[int, int]) -> List[Path]:
    """
    Circuits between pairs, each pair is denoted by it's pair = donor index
    """
    donor_to_compatible_donor_graph = _get_donor_to_compatible_donor_graph(n_donors,
                                                                           compatible_donor_idxs_per_donor_idx)
    all_circuits = []
    for i, circuit in enumerate(topology.all_circuits(donor_to_compatible_donor_graph)):
        if _circuit_valid(circuit, config_parameters, donors, original_donor_idx_to_recipient_idx):
            circuit_with_end = tuple(list(circuit) + [circuit[0]])
            all_circuits.append(circuit_with_end)
        if i > config_parameters.max_cycles_in_all_solutions_solver:
            raise TooComplicatedDataForAllSolutionsSolver(
                f'Number of possible cycles in data was above threshold of '
                f'{config_parameters.max_cycles_in_all_solutions_solver})')

    return all_circuits


def _circuit_valid(circuit: Path, config_parameters: ConfigParameters, donors: List[Donor],
                   original_donor_idx_to_recipient_idx: Dict[int, int]):
    return (
            len(circuit) <= config_parameters.max_cycle_length
            and country_count_in_path(circuit, donors) <= config_parameters.max_number_of_distinct_countries_in_round
            and _no_duplicate_recipients_in_path(circuit, original_donor_idx_to_recipient_idx)

    )


def _no_duplicate_recipients_in_path(path: Path, original_donor_idx_to_recipient_idx: Dict[int, int]):
    return len(path) == len({original_donor_idx_to_recipient_idx[donor_idx] for donor_idx in path})


def find_all_sequences(compatible_donor_idxs_per_donor_idx: Dict[int, List[int]],
                       max_length: int,
                       donors: List[Donor],
                       max_countries: int,
                       original_donor_idx_to_recipient_idx: Dict[int, int]) -> List[Path]:
    bridge_indices = _get_bridge_indices(original_donor_idx_to_recipient_idx)

    paths = []

    for bridge_index in bridge_indices:
        bridge_paths = _find_all_paths_starting_with(bridge_index, compatible_donor_idxs_per_donor_idx, set())
        paths.extend(bridge_paths)

    paths = [tuple(path) for path in paths if 1 < len(path) <= max_length + 1 and
             country_count_in_path(tuple(path), donors) <= max_countries and
             _no_duplicate_recipients_in_path(tuple(path), original_donor_idx_to_recipient_idx)]

    return paths


def country_count_in_path(path: Path, donors: List[Donor]) -> int:
    return len({donors[donor_idx].parameters.country_code for donor_idx in path})


def keep_only_highest_scoring_paths(paths: List[Path],
                                    compatibility_graph: CompatibilityGraph,
                                    donor_idx_to_recipient_idx: Dict[int, int],
                                    donors: List[Donor],
                                    is_cycle: bool) -> List[PathWithScore]:
    def group_key(path: Path) -> List[int]:
        return sorted(list(set(path)))

    paths_grouped = [list(group) for _, group in groupby(sorted(paths, key=group_key), group_key)]

    paths_filtered = [
        max(path_group,
            key=lambda path: _get_path_score(compatibility_graph, path, donor_idx_to_recipient_idx))
        for path_group in paths_grouped]
    return [PathWithScore(
        path,
        _get_path_score(compatibility_graph, path, donor_idx_to_recipient_idx),
        _get_path_debt(is_cycle, path, donors),
        _get_path_debt(is_cycle, path, donors, blood_group_zero=True),
        _get_path_length(is_cycle, path)
    ) for path in
        paths_filtered]


def _get_path_length(is_cycle: bool, path: Path) -> int:
    length = len(path) - 1 if is_cycle else len(path)
    return length


def _get_path_debt(is_cycle: bool, path: Path, donors: List[Donor], blood_group_zero=False) -> Dict[Country, int]:
    path_debt = {}
    if is_cycle:
        return path_debt
    current_bridging_donor = donors[path[0]]
    future_bridging_donor = donors[path[-1]]
    if current_bridging_donor.parameters.blood_group.ZERO == BloodGroup.ZERO or not blood_group_zero:
        path_debt[current_bridging_donor.parameters.country_code] = 1
    if future_bridging_donor.parameters.blood_group.ZERO == BloodGroup.ZERO or not blood_group_zero:
        path_debt[future_bridging_donor.parameters.country_code] = \
            path_debt.get(future_bridging_donor.parameters.country_code, 0) - 1
    return path_debt


def _get_path_score(compatibility_graph: CompatibilityGraph,
                    path: Path,
                    donor_idx_to_recipient_idx: Dict[int, int]) -> int:
    pairs = _get_pairs_from_paths([path], donor_idx_to_recipient_idx)
    return get_score_for_idx_pairs(compatibility_graph, pairs)


def get_pairs_from_clique(clique,
                          path_number_to_path: Dict[int, PathWithScore],
                          donor_idx_to_recipient_idx: Dict[int, int]) -> List[DonorRecipientPairIdxOnly]:
    circuit_list = [path_number_to_path[path_number].donor_ids for path_number in clique]

    return _get_pairs_from_paths(circuit_list, donor_idx_to_recipient_idx)


def _get_pairs_from_paths(paths: List[Path],
                          pair_index_to_recipient_index: Dict[int, int]) -> List[DonorRecipientPairIdxOnly]:
    return [pair for path in paths for pair in _get_pairs_from_path(path, pair_index_to_recipient_index)]


def _get_pairs_from_path(path: Path, pair_index_to_recipient_index: Dict[int, int]) -> List[DonorRecipientPairIdxOnly]:
    return [DonorRecipientPairIdxOnly(path[i], pair_index_to_recipient_index[path[i + 1]]) for i in
            range(len(path) - 1)]


# pylint: disable=too-many-locals
# I think here the local variables help the code
def find_paths_with_same_donors(all_paths: List[PathWithScore],
                                original_donor_idx_to_recipient_idx: Dict[int, int]
                                ) -> Tuple[List[List[int]], Dict[int, PathWithScore]]:
    path_id_to_path = dict(enumerate(all_paths))

    donor_ids = {donor_id for path in all_paths for donor_id in path.donor_ids}
    paths_with_the_same_donors = []
    for donor_id in donor_ids:
        paths_for_donor = [path_id for path_id, path in path_id_to_path.items() if
                           _donor_id_or_its_recipient_in_path(donor_id, path, original_donor_idx_to_recipient_idx)]
        if len(paths_for_donor) > 1:
            paths_with_the_same_donors.append(paths_for_donor)

    return paths_with_the_same_donors, path_id_to_path


def _donor_id_or_its_recipient_in_path(donor_id, path: PathWithScore,
                                       original_donor_idx_to_recipient_idx: Dict[int, int]):
    donor_in_path = donor_id in path.donor_ids
    donors_recipient_in_path = original_donor_idx_to_recipient_idx[donor_id] in [
        original_donor_idx_to_recipient_idx[donor_id] for donor_id in path.donor_ids]
    return donor_in_path or donors_recipient_in_path


# pylint: enable=too-many-locals


def _find_acceptable_recipient_idxs(compatibility_graph: CompatibilityGraph, donor_index: int) -> List[int]:
    return list({pair[1] for pair in compatibility_graph.keys() if pair[0] == donor_index})


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


def _get_bridge_indices(donor_idx_to_recipient_idx: Dict[int, int]) -> List[int]:
    bridge_indices = {donor_id for donor_id, recipient_id in donor_idx_to_recipient_idx.items() if recipient_id == -1}
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
