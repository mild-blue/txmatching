import logging
from typing import Dict, Iterable, List

from graph_tool import topology

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.solvers.all_solutions_solver.compatibility_graph_utils import (
    Path, construct_path_intersection_graph, find_all_cycles,
    find_all_sequences, get_compatible_donor_idxs_per_donor_idx,
    get_pairs_from_clique, keep_only_highest_scoring_paths)
from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly

logger = logging.getLogger(__name__)


def find_possible_path_combinations_from_compatibility_graph(compatibility_graph: CompatibilityGraph,
                                                             donor_idx_to_recipient_idx: Dict[int, int],
                                                             donors: List[Donor],
                                                             config_parameters: ConfigParameters = ConfigParameters(),
                                                             ) -> Iterable[List[DonorRecipientPairIdxOnly]]:
    """
    Returns iterator over the optimal list of possible path combinations. The result is a list of pairs. Each pair
    consists of two integers which correspond to recipient and donor indices.
    """
    if len(compatibility_graph) == 0:
        logger.info('Empty set of paths, returning empty iterator')
        yield from ()
        return

    highest_scoring_paths = get_highest_scoring_paths(compatibility_graph,
                                                      donor_idx_to_recipient_idx,
                                                      donors,
                                                      config_parameters)

    if len(highest_scoring_paths) == 0:
        logger.info('Empty set of paths, returning empty iterator')
        yield from ()
        return

    logger.info(f'Constructing intersection graph # paths {len(highest_scoring_paths)}')
    path_intersections_graph, path_number_to_path = construct_path_intersection_graph(highest_scoring_paths)
    unused_path_numbers = {path_intersections_graph.vertex_index[path_number] for path_number in
                           path_number_to_path.keys()}

    logger.info('Listing all max cliques')

    # TODO: Fix this properly https://trello.com/c/0GBzQWt2
    if len(list(path_intersections_graph.vertices())) > 0:
        max_cliques = topology.max_cliques(path_intersections_graph)
    else:
        max_cliques = []

    logger.info('Creating pairings from paths and circuits ')

    for clique in max_cliques:
        unused_path_numbers.difference_update(clique)
        yield get_pairs_from_clique(clique, path_number_to_path, donor_idx_to_recipient_idx)

    single_vertex_cliques = [[path_number] for path_number in unused_path_numbers]
    for clique in single_vertex_cliques:
        yield get_pairs_from_clique(clique,
                                    path_number_to_path,
                                    donor_idx_to_recipient_idx)


def get_highest_scoring_paths(compatibility_graph: CompatibilityGraph,
                              donor_idx_to_recipient_idx: Dict[int, int],
                              donors: List[Donor],
                              config_parameters: ConfigParameters = ConfigParameters()) -> List[Path]:
    n_donors = len(donor_idx_to_recipient_idx)
    assert len(donors) == n_donors

    compatible_donor_idxs_per_donor_idx = get_compatible_donor_idxs_per_donor_idx(compatibility_graph,
                                                                                  donor_idx_to_recipient_idx)

    cycles = find_all_cycles(n_donors,
                             compatible_donor_idxs_per_donor_idx,
                             donors,
                             config_parameters)

    sequences = find_all_sequences(compatible_donor_idxs_per_donor_idx,
                                   config_parameters.max_sequence_length,
                                   donors,
                                   config_parameters.max_number_of_distinct_countries_in_round,
                                   donor_idx_to_recipient_idx)

    highest_scoring_paths = keep_only_highest_scoring_paths(
        cycles,
        compatibility_graph=compatibility_graph,
        donor_idx_to_recipient_idx=donor_idx_to_recipient_idx
    ) + keep_only_highest_scoring_paths(
        sequences,
        compatibility_graph=compatibility_graph,
        donor_idx_to_recipient_idx=donor_idx_to_recipient_idx
    )
    return highest_scoring_paths