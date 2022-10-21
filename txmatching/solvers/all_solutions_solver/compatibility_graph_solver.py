import logging
from typing import Dict, Iterable, List

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, Recipient
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.solvers.all_solutions_solver.compatibility_graph_utils import (
    PathWithScore, find_all_cycles, find_all_sequences,
    find_paths_with_same_donors, get_donor_to_compatible_donor_graph,
    get_compatible_donor_idxs_per_donor_idx, get_pairs_from_clique,
    keep_only_highest_scoring_paths)
from txmatching.solvers.all_solutions_solver.optimise_paths import \
    optimise_paths
from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly

logger = logging.getLogger(__name__)


# This should be improved.
# pylint:disable=too-many-arguments)
def find_optimal_paths(compatibility_graph: CompatibilityGraph,
                       original_donor_idx_to_recipient_idx: Dict[int, int],
                       donors: List[Donor],
                       recipients: List[Recipient],
                       config_parameters: ConfigParameters = ConfigParameters(),
                       required_donors_ids_per_required_recipient: List[List[int]] = None
                       ) -> Iterable[List[DonorRecipientPairIdxOnly]]:
    """
    Returns iterator over the optimal list of possible path combinations. The result is a list of pairs. Each pair
    consists of two integers which correspond to recipient and donor indices.
    """
    if required_donors_ids_per_required_recipient is None:
        required_donors_ids_per_required_recipient = []
    if len(compatibility_graph) == 0:
        logger.info('Empty set of paths, returning empty iterator')
        yield from ()
        return

    highest_scoring_paths = get_highest_scoring_paths(compatibility_graph,
                                                      original_donor_idx_to_recipient_idx,
                                                      donors,
                                                      recipients,
                                                      config_parameters)

    if len(highest_scoring_paths) == 0:
        logger.info('Empty set of paths, returning empty iterator')
        yield from ()
        return

    logger.info(f'Constructing intersection graph # paths {len(highest_scoring_paths)}')
    paths_idx_with_the_same_donors, path_id_to_path_with_score, required_paths_per_required_recipient = \
        find_paths_with_same_donors(
            highest_scoring_paths,
            original_donor_idx_to_recipient_idx,
            required_donors_ids_per_required_recipient
        )

    found_solutions = optimise_paths(paths_idx_with_the_same_donors, path_id_to_path_with_score, config_parameters,
                                     required_paths_per_required_recipient)
    for selected_cycles in found_solutions:
        yield get_pairs_from_clique(selected_cycles, path_id_to_path_with_score, original_donor_idx_to_recipient_idx)


def get_highest_scoring_paths(compatibility_graph: CompatibilityGraph,
                              original_donor_idx_to_recipient_idx: Dict[int, int],
                              donors: List[Donor],
                              recipients: List[Recipient],
                              config_parameters: ConfigParameters = ConfigParameters()) -> List[PathWithScore]:
    n_donors = len(original_donor_idx_to_recipient_idx)
    assert len(donors) == n_donors

    compatible_donor_idxs_per_donor_idx = get_compatible_donor_idxs_per_donor_idx(compatibility_graph,
                                                                                  original_donor_idx_to_recipient_idx)

    donor_to_compatible_donor_graph = get_donor_to_compatible_donor_graph(original_donor_idx_to_recipient_idx,
                                                                          compatible_donor_idxs_per_donor_idx)

    cycles = find_all_cycles(donor_to_compatible_donor_graph,
                             donors,
                             config_parameters,
                             original_donor_idx_to_recipient_idx,
                             config_parameters.max_cycle_length)

    sequences = find_all_sequences(donor_to_compatible_donor_graph,
                                   config_parameters.max_sequence_length,
                                   donors,
                                   config_parameters.max_number_of_distinct_countries_in_round,
                                   original_donor_idx_to_recipient_idx)

    highest_scoring_paths = keep_only_highest_scoring_paths(
        cycles,
        compatibility_graph=compatibility_graph,
        donor_idx_to_recipient_idx=original_donor_idx_to_recipient_idx,
        donors=donors,
        recipients=recipients
    ) + keep_only_highest_scoring_paths(
        sequences,
        compatibility_graph=compatibility_graph,
        donor_idx_to_recipient_idx=original_donor_idx_to_recipient_idx,
        donors=donors,
        recipients=recipients
    )
    return highest_scoring_paths
