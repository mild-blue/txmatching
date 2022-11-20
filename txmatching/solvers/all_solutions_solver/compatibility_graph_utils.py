import dataclasses
import logging
from itertools import groupby
from typing import Dict, List, Tuple

import networkx as nx

from txmatching.auth.exceptions import TooComplicatedDataForAllSolutionsSolver
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, Recipient
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
    recipient_idxs = set(
        recipient_idx for recipient_idx in original_donor_idx_to_recipient_idx.values() if recipient_idx != -1)

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


def find_all_cycles(donor_to_compatible_donor_graph: nx.Graph,
                    donors: List[Donor],
                    config_parameters: ConfigParameters,
                    original_donor_idx_to_recipient_idx: Dict[int, int],
                    max_cycle_length: int) -> List[Path]:
    """
    Circuits between pairs, each pair is denoted by it's pair = donor index
    """
    if max_cycle_length < 2:
        return []

    non_directed_donors_dict = nx.get_node_attributes(donor_to_compatible_donor_graph, 'ndd')
    all_circuits = []
    for node in donor_to_compatible_donor_graph.nodes():
        if non_directed_donors_dict[node] is False:
            # returns cycles with the same first and last node
            _find_cycles_recursive(node, [], all_circuits, max_cycle_length, donor_to_compatible_donor_graph,
                                   config_parameters.max_cycles_in_all_solutions_solver)

    circuits_to_return = []
    for circuit in all_circuits:
        if _circuit_valid(circuit[:-1], config_parameters, donors, original_donor_idx_to_recipient_idx):
            circuits_to_return.append(circuit)

    return circuits_to_return


# pylint: disable=too-many-arguments
def _find_cycles_recursive(node: int, maybe_cycle: List[int], all_cycles: List[Path], max_cycle_length: int,
                           graph: nx.Graph, max_cycles_in_all_solutions_solver: int):
    if len(maybe_cycle) >= 1:
        if node == maybe_cycle[0]:
            maybe_cycle_copy = maybe_cycle.copy()
            all_cycles.append(tuple(maybe_cycle_copy + [maybe_cycle_copy[0]]))
            if len(all_cycles) > max_cycles_in_all_solutions_solver:
                raise TooComplicatedDataForAllSolutionsSolver(
                    f'Number of possible cycles in data was above threshold of '
                    f'{max_cycles_in_all_solutions_solver})')
            return

        if len(maybe_cycle) == max_cycle_length:
            return

        # this prevents duplicate cycles to be found
        if node < maybe_cycle[0]:
            return

    if node in maybe_cycle:
        return

    maybe_cycle.append(node)

    for neighbor in graph.neighbors(node):
        _find_cycles_recursive(neighbor, maybe_cycle.copy(), all_cycles, max_cycle_length, graph,
                               max_cycles_in_all_solutions_solver)


def _circuit_valid(circuit: Path, config_parameters: ConfigParameters, donors: List[Donor],
                   original_donor_idx_to_recipient_idx: Dict[int, int]):
    return (
            country_count_in_path(circuit, donors) <= config_parameters.max_number_of_distinct_countries_in_round
            and _no_duplicate_recipients_in_path(circuit, original_donor_idx_to_recipient_idx)
    )


def _no_duplicate_recipients_in_path(path: Path, original_donor_idx_to_recipient_idx: Dict[int, int]):
    return len(path) == len({original_donor_idx_to_recipient_idx[donor_idx] for donor_idx in path})


def find_chains_with_same_recipients_at_the_end(all_paths: List[PathWithScore],
                                                original_donor_idx_to_recipient_idx: Dict[int, int],
                                                ) -> Dict[int, List[int]]:
    path_id_to_path = dict(enumerate(all_paths))
    path_ids = path_id_to_path.keys()
    chains_with_the_same_recipients = {path_id: set() for path_id in path_ids}

    for path_id in path_ids:
        # if path is a chain
        if path_id_to_path[path_id].donor_ids[0] != path_id_to_path[path_id].donor_ids[-1]:
            for inner_path_id in path_ids:
                if _chains_are_the_same_with_same_recipient_at_the_end(path_id_to_path[path_id],
                                                                       path_id_to_path[inner_path_id],
                                                                       original_donor_idx_to_recipient_idx):
                    chains_with_the_same_recipients[path_id].add(inner_path_id)
                    chains_with_the_same_recipients[inner_path_id].add(path_id)

    return chains_with_the_same_recipients


def _chains_are_the_same_with_same_recipient_at_the_end(path_1: PathWithScore, path_2: PathWithScore,
                                                        original_donor_idx_to_recipient_idx: Dict[int, int]) -> bool:
    if original_donor_idx_to_recipient_idx[path_1.donor_ids[-1]] == original_donor_idx_to_recipient_idx[
        path_2.donor_ids[-1]] and path_1.donor_ids[:-1] == path_2.donor_ids[:-1]:
        return True
    return False


def find_all_sequences(donor_to_compatible_donor_graph: nx.Graph,
                       max_chain_length: int,
                       donors: List[Donor],
                       max_countries: int,
                       original_donor_idx_to_recipient_idx: Dict[int, int]) -> List[Path]:
    if max_chain_length < 1:
        return []

    non_directed_donors_dict = nx.get_node_attributes(donor_to_compatible_donor_graph, 'ndd')
    all_sequences = []
    for node in donor_to_compatible_donor_graph.nodes():
        if non_directed_donors_dict[node] is True:
            _find_sequences_recursive(node, [], all_sequences, max_chain_length, donor_to_compatible_donor_graph)

    all_sequences = [sequence for sequence in all_sequences if 1 < len(sequence) <= max_chain_length + 1 and
                     country_count_in_path(sequence, donors) <= max_countries and
                     _no_duplicate_recipients_in_path(sequence, original_donor_idx_to_recipient_idx)]

    return all_sequences


def _find_sequences_recursive(node: int, maybe_sequence: List[int], all_sequences: List[Path], max_chain_length: int,
                              graph: nx.Graph):
    if node in maybe_sequence:
        return

    maybe_sequence.append(node)

    if len(maybe_sequence) > max_chain_length + 1:
        return

    if len(maybe_sequence) >= 2:
        all_sequences.append(tuple(maybe_sequence.copy()))

    for neighbor in graph.neighbors(node):
        _find_sequences_recursive(neighbor, maybe_sequence.copy(), all_sequences, max_chain_length, graph)


def country_count_in_path(path: Path, donors: List[Donor]) -> int:
    return len({donors[donor_idx].parameters.country_code for donor_idx in path})


def keep_only_highest_scoring_paths(paths: List[Path],
                                    compatibility_graph: CompatibilityGraph,
                                    donor_idx_to_recipient_idx: Dict[int, int],
                                    donors: List[Donor],
                                    recipients: List[Recipient]) -> List[PathWithScore]:
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
        _get_path_debt(path, donor_idx_to_recipient_idx, donors, recipients),
        _get_path_debt(path, donor_idx_to_recipient_idx, donors, recipients, blood_group_zero=True),
        _get_path_length(path)
    ) for path in
        paths_filtered]


def _get_path_length(path: Path) -> int:
    return len(path) - 1


def _get_path_debt(path: Path,
                   donor_idx_to_recipient_idx: Dict[int, int],
                   donors: List[Donor],
                   recipients: List[Recipient], blood_group_zero=False) -> Dict[Country, int]:
    path_donors = path[:-1]
    path_recipients = [donor_idx_to_recipient_idx[donor_idx] for donor_idx in path[1:]]

    donor_countries = [donors[donor_idx].parameters.country_code for donor_idx in path_donors
                       if not blood_group_zero or donors[donor_idx].parameters.blood_group == BloodGroup.ZERO]
    if not blood_group_zero:
        recipient_countries = [recipients[recipient_idx].parameters.country_code for recipient_idx in path_recipients]
    else:
        recipient_countries = [recipients[recipient_idx].parameters.country_code for recipient_idx, donor_idx in
                               zip(path_recipients, path_donors)
                               if donors[donor_idx].parameters.blood_group == BloodGroup.ZERO]
    path_debt = {}
    for donor_country in donor_countries:
        path_debt[donor_country] = path_debt.get(donor_country, 0) + 1
    for recipient_country in recipient_countries:
        path_debt[recipient_country] = path_debt.get(recipient_country, 0) - 1
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
                                original_donor_idx_to_recipient_idx: Dict[int, int],
                                required_donor_idxs_per_required_recipients: List[List[int]]
                                ) -> Tuple[Dict[int, List[int]], Dict[int, PathWithScore], List[List[int]]]:
    path_id_to_path = dict(enumerate(all_paths))

    donor_ids = {donor_id for path in all_paths for donor_id in path.donor_ids}
    paths_with_the_same_donors = {}
    for donor_id in donor_ids:
        paths_for_donor = [path_id for path_id, path in path_id_to_path.items() if
                           _donor_id_or_its_recipient_in_path(donor_id, path, original_donor_idx_to_recipient_idx)]
        if len(paths_for_donor) > 1:
            paths_with_the_same_donors[donor_id] = paths_for_donor
    required_paths_per_recipient = []

    for required_donor_idxs_per_required_recipient in required_donor_idxs_per_required_recipients:
        paths_idxs_per_donor = []
        for donor_idx in required_donor_idxs_per_required_recipient:
            paths_idxs_per_donor.append(
                {path_id for path_id, path in path_id_to_path.items() if donor_idx in path.donor_ids})
        required_paths = set.union(*paths_idxs_per_donor)
        required_paths_per_recipient.append(required_paths)

    return paths_with_the_same_donors, path_id_to_path, required_paths_per_recipient


def _donor_id_or_its_recipient_in_path(donor_id: int, path: PathWithScore,
                                       original_donor_idx_to_recipient_idx: Dict[int, int]) -> bool:
    donor_in_path = donor_id in path.donor_ids
    donors_recipient_in_path = _is_recipient_id_in_path(original_donor_idx_to_recipient_idx[donor_id],
                                                        path,
                                                        original_donor_idx_to_recipient_idx)

    return donor_in_path or donors_recipient_in_path


def _is_recipient_id_in_path(recipient_id, path: PathWithScore, original_donor_idx_to_recipient_idx: Dict[int, int]):
    # if recipient id is -1 its not real donor and we ignore it
    if recipient_id < 0:
        return False
    return recipient_id in [original_donor_idx_to_recipient_idx[donor_id] for donor_id in path.donor_ids]


# pylint: enable=too-many-locals
def _find_acceptable_recipient_idxs(compatibility_graph: CompatibilityGraph, donor_index: int) -> List[int]:
    return list({pair[1] for pair in compatibility_graph.keys() if pair[0] == donor_index})


def get_donor_to_compatible_donor_graph(original_donor_idx_to_recipient_idx: Dict[int, int],
                                        compatible_donor_idxs_per_donor_idx: Dict[int, List[int]]) -> nx.Graph:
    donor_to_compatible_donor_graph = nx.DiGraph()
    non_directed_donors = {donor_id for donor_id in original_donor_idx_to_recipient_idx.keys() if
                           original_donor_idx_to_recipient_idx[donor_id] == -1}

    donor_to_compatible_donor_graph.add_nodes_from(
        [(donor_id, {'ndd': donor_id in non_directed_donors}) for donor_id in
         compatible_donor_idxs_per_donor_idx.keys()])

    # Add donor -> compatible_donor edges
    for donor_idx, compatible_donor_idxs in compatible_donor_idxs_per_donor_idx.items():
        donor_to_compatible_donor_graph.add_edges_from(
            (donor_idx, compatible_donor_idx)
            for compatible_donor_idx in compatible_donor_idxs
        )
    return donor_to_compatible_donor_graph
