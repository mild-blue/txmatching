import logging
from typing import Dict, List, Tuple

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, DonorType, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver

logger = logging.getLogger(__name__)


def prepare_data_for_ilp(active_donors_dict: Dict[DonorDbId, Donor],
                         active_recipients_dict: Dict[RecipientDbId, Recipient],
                         configuration: Configuration) -> DataAndConfigurationForILPSolver:
    scorer = scorer_from_configuration(configuration)

    score_matrix = []
    for donor in active_donors_dict.values():
        row = []
        for donor_for_recipient in active_donors_dict.values():

            if donor_for_recipient.related_recipient_db_id and donor.db_id != donor_for_recipient.db_id:
                recipient = active_recipients_dict[donor_for_recipient.related_recipient_db_id]
                score = scorer.score_transplant_including_original_tuple(donor, recipient, donor_for_recipient)
                row.append(score)
            else:
                row.append(-1)

        score_matrix.append(row)

    bridging_donors = [i for i, donor in enumerate(active_donors_dict.values()) if
                       donor.donor_type != DonorType.DONOR]

    return DataAndConfigurationForILPSolver(
        num_nodes=len(score_matrix),
        non_directed_donors=bridging_donors,
        max_sequence_length=configuration.max_sequence_length,
        max_cycle_length=configuration.max_cycle_length,
        edges=_create_edges(score_matrix),
    )


def _create_edges(score_matrix: List[List[int]]) -> List[Tuple[int, int, int]]:
    num_nodes = len(score_matrix)
    edges = []
    for from_node in range(0, num_nodes):
        for to_node in range(0, num_nodes):
            weight = int(score_matrix[from_node][to_node])
            if weight >= 0:
                edges.append((from_node, to_node, weight))
    return edges
