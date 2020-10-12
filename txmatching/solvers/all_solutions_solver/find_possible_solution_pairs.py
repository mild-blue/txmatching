import logging
from typing import Iterable, List

import numpy as np
from graph_tool import topology

from txmatching.solve_service.data_objects.donor_recipient import \
    DonorIdRecipientIdPair
from txmatching.solvers.all_solutions_solver.helper_functions import (
    construct_intersection_graph, construct_pair_index_to_recipient_index,
    find_all_bridge_paths, find_all_circuits, get_pairs_from_clique,
    graph_from_score_matrix, keep_only_highest_scoring_paths)

logger = logging.getLogger(__name__)


def find_possible_solution_pairs_from_score_matrix(score_matrix: np.ndarray) -> Iterable[List[DonorIdRecipientIdPair]]:
    """
    Returns iterator over the optimal matching. The result is a list of pairs. Each pair consists of two integers
    which correspond to recipient, donor indices in the self._donors, resp. self._recipients lists.

    :param score_matrix: matrix of Score(i,j) for transplant from donor_i to recipient_j
        special values are:
        UNACCEPTABLE_SCORE = np.NINF
        DEFAULT_DONOR_RECIPIENT_PAIR_SCORE = np.NAN
    """
    graph, _ = graph_from_score_matrix(score_matrix)
    pair_index_to_recipient_index = construct_pair_index_to_recipient_index(score_matrix)
    pure_circuits = find_all_circuits(graph)
    bridge_paths = find_all_bridge_paths(score_matrix)

    all_paths = keep_only_highest_scoring_paths(score_matrix=score_matrix,
                                                pure_circuits=pure_circuits,
                                                bridge_paths=bridge_paths,
                                                pair_index_to_recipient_index=pair_index_to_recipient_index)

    if len(all_paths) == 0:
        logger.info('Empty set of paths, returning empty iterator')
        yield from ()
        return

    logger.info(f'Constructing intersection graph, '
                f'#circuits: {len(pure_circuits)}, #paths: {len(bridge_paths)} initially, filtered to {len(all_paths)}')
    intersection_graph, path_number_to_path = construct_intersection_graph(all_paths)
    unused_path_numbers = {intersection_graph.vertex_index[path_number] for path_number in
                           path_number_to_path.keys()}

    logger.info('Listing all max cliques')

    # TODO: Fix this properly https://trello.com/c/0GBzQWt2
    if len(list(intersection_graph.vertices())) > 0:
        max_cliques = topology.max_cliques(intersection_graph)
    else:
        max_cliques = []

    logger.info('Creating pairings from paths and circuits ')

    for clique in max_cliques:
        unused_path_numbers.difference_update(clique)
        yield get_pairs_from_clique(clique,
                                    path_number_to_path,
                                    pure_circuits,
                                    pair_index_to_recipient_index)

    single_vertex_cliques = [[path_number] for path_number in unused_path_numbers]
    for clique in single_vertex_cliques:
        yield get_pairs_from_clique(clique,
                                    path_number_to_path,
                                    pure_circuits,
                                    pair_index_to_recipient_index)
