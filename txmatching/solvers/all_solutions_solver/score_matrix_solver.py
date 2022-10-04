import logging
from typing import Dict, Iterable, List, Tuple

import numpy as np
from graph_tool import topology

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, Recipient
from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.all_solutions_solver.score_matrix_utils import (
    Path, construct_path_intersection_graph, find_all_cycles,
    find_all_sequences, get_compatible_donor_idxs_per_donor_idx,
    get_donor_idx_to_recipient_idx, get_pairs_from_clique,
    keep_only_highest_scoring_paths)

logger = logging.getLogger(__name__)


def find_possible_path_combinations_from_score_matrix(score_matrix: np.ndarray,
                                                      donors: List[Donor],
                                                      config_parameters: ConfigParameters = ConfigParameters(),
                                                      ) -> Iterable[List[DonorRecipientPairIdxOnly]]:
    """
    Returns iterator over the optimal list of possible path combinations. The result is a list of pairs. Each pair
    consists of two integers which correspond to recipient and donor indices.

    :param score_matrix: matrix of Score(i,j) for transplant from donor_i to recipient_j
            special values are:
    ORIGINAL_DONOR_RECIPIENT_SCORE = -2.0
    TRANSPLANT_IMPOSSIBLE_SCORE = -1.0
    :param donors: List of all possible donors
    :param config_parameters
    """
    if len(score_matrix) == 0:
        logger.info('Empty set of paths, returning empty iterator')
        yield from ()
        return

    donor_idx_to_recipient_idx = get_donor_idx_to_recipient_idx(score_matrix)
    donor_idx_to_recipient_idx, highest_scoring_paths = get_highest_scoring_paths(score_matrix,
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
    
    #the problem is somewhere here - cycles are good, so it must be here
    for clique in max_cliques:
        unused_path_numbers.difference_update(clique)
        pairs = get_pairs_from_clique(clique, path_number_to_path, donor_idx_to_recipient_idx)
        yield pairs
    logger.info("bla")
    single_vertex_cliques = [[path_number] for path_number in unused_path_numbers]
    for clique in single_vertex_cliques:
        pairs = get_pairs_from_clique(clique,
                                    path_number_to_path,
                                    donor_idx_to_recipient_idx)
        yield pairs
    logger.info("bla")

def get_highest_scoring_paths(score_matrix: np.ndarray,
                              donor_idx_to_recipient_idx: Dict[int, int],
                              donors: List[Donor],
                              config_parameters: ConfigParameters = ConfigParameters()) -> Tuple[Dict[int, int], List[Path]]:
    n_donors, _ = score_matrix.shape
    assert len(donors) == n_donors

    compatible_donor_idxs_per_donor_idx = get_compatible_donor_idxs_per_donor_idx(score_matrix,
                                                                                  donor_idx_to_recipient_idx)

    cycles = find_all_cycles(n_donors,
                             compatible_donor_idxs_per_donor_idx,
                             donors,
                             config_parameters)

    sequences = find_all_sequences(score_matrix,
                                   compatible_donor_idxs_per_donor_idx,
                                   config_parameters.max_sequence_length,
                                   donors,
                                   config_parameters.max_number_of_distinct_countries_in_round)

    
    # TODO: MUZEME SE POKOUSIT ODFILTROVAT NEVALIDNI PARY I Z donor_idx_to_recipient_idx

    donor_idx_to_recipient_idx, valid_cycles = _filter_cycles_with_recipient_duplicates(donor_idx_to_recipient_idx, cycles)
    

    highest_scoring_paths = keep_only_highest_scoring_paths( # pada zde 
        valid_cycles,
        score_matrix=score_matrix,
        donor_idx_to_recipient_idx=donor_idx_to_recipient_idx
    ) + keep_only_highest_scoring_paths(
        sequences,
        score_matrix=score_matrix,
        donor_idx_to_recipient_idx=donor_idx_to_recipient_idx
    )
    return donor_idx_to_recipient_idx, highest_scoring_paths


def _filter_cycles_with_recipient_duplicates(donor_idx_to_recipient_idx: Dict[int, int], cycles: List[Path]) -> Tuple[Dict[int, int], List[Path]]:
    cycles_with_recipients = [[[donor_idx, donor_idx_to_recipient_idx[donor_idx]]
                               for donor_idx in cycle] for cycle in cycles]
    valid_cycles = []
    for cycle in cycles_with_recipients:
        recipient_ids = [pair[1] for pair in cycle]
        recipient_ids.pop()
        unique_recipients = set(recipient_ids)
        if len(unique_recipients) == len(recipient_ids):
            valid_cycles.append(cycle)

    # get list of all recipients from valid cycles
    # all_donor_recipients = [pair for cycle in valid_cycles for pair in cycle[:-1]]
    # seen_recipients = []
    # for pair in all_donor_recipients:
    #     if pair[1] in seen_recipients:
    #         donor_idx_to_recipient_idx.pop(pair[0])
    #     else:
    #         seen_recipients.append(pair[1])

    valid_cycles = [tuple(donor_idx for donor_idx, _ in cycle) for cycle in valid_cycles]

    return donor_idx_to_recipient_idx, valid_cycles


    # remove pairs from donor_idx_to_recipient_idx
    '''
    if recipient is twice in the group of cycles then remove the second pair from donor_idx_to_recipient_idx
    '''
    # seen_recipients = set()
    # for cycle in valid_cycles:
    #     recipient_ids = [pair[1] for pair in cycle]
    #     recipient_ids.pop()
    #     dup = [x for x in recipient_ids if recipient_ids.count(x) > 1]
    #     if len(dup) > 0:
    #         for pair in cycle:
    #             if pair[1] in dup:
    #                 donor_idx_to_recipient_idx.pop(pair[0]) #invalid pop
    #                 break