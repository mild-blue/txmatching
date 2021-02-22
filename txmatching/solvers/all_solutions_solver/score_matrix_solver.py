import logging
from typing import Dict, Iterable, List

import numpy as np
from graph_tool import topology

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor
from txmatching.solvers.all_solutions_solver.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.all_solutions_solver.score_matrix_utils import (
    Path, construct_path_intersection_graph, find_all_cycles,
    find_all_sequences, get_compatible_donor_idxs_per_donor_idx,
    get_donor_idx_to_recipient_idx, get_pairs_from_clique,
    keep_only_highest_scoring_paths)

logger = logging.getLogger(__name__)


def find_possible_path_combinations_from_score_matrix(score_matrix: np.ndarray,
                                                      donors: List[Donor],
                                                      configuration: Configuration = Configuration(),
                                                      ) -> Iterable[List[DonorRecipientPairIdxOnly]]:
    """
    Returns iterator over the optimal list of possible path combinations. The result is a list of pairs. Each pair
    consists of two integers which correspond to recipient and donor indices.

    :param score_matrix: matrix of Score(i,j) for transplant from donor_i to recipient_j
            special values are:
    ORIGINAL_DONOR_RECIPIENT_SCORE = -2.0
    TRANSPLANT_IMPOSSIBLE_SCORE = -1.0
    :param donors: List of all possible donors
    :param configuration
    """
    if len(score_matrix) == 0:
        logger.info('Empty set of paths, returning empty iterator')
        yield from ()
        return

    donor_idx_to_recipient_idx = get_donor_idx_to_recipient_idx(score_matrix)
    highest_scoring_paths = get_highest_scoring_paths(score_matrix,
                                                      donor_idx_to_recipient_idx,
                                                      donors,
                                                      configuration)

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


def get_highest_scoring_paths(score_matrix: np.ndarray,
                              donor_idx_to_recipient_idx: Dict[int, int],
                              donors: List[Donor],
                              configuration: Configuration = Configuration()) -> List[Path]:
    n_donors, _ = score_matrix.shape
    assert len(donors) == n_donors

    compatible_donor_idxs_per_donor_idx = get_compatible_donor_idxs_per_donor_idx(score_matrix,
                                                                                  donor_idx_to_recipient_idx)

    cycles = find_all_cycles(n_donors,
                             compatible_donor_idxs_per_donor_idx,
                             configuration.max_cycle_length,
                             donors,
                             configuration.max_number_of_distinct_countries_in_round,
                             configuration.max_allowed_number_of_circuits)

    sequences = find_all_sequences(score_matrix,
                                   compatible_donor_idxs_per_donor_idx,
                                   configuration.max_sequence_length,
                                   donors,
                                   configuration.max_number_of_distinct_countries_in_round)

    highest_scoring_paths = keep_only_highest_scoring_paths(
        cycles,
        score_matrix=score_matrix,
        donor_idx_to_recipient_idx=donor_idx_to_recipient_idx
    ) + keep_only_highest_scoring_paths(
        sequences,
        score_matrix=score_matrix,
        donor_idx_to_recipient_idx=donor_idx_to_recipient_idx
    )
    return highest_scoring_paths
