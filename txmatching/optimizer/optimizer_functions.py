import networkx as nx
import numpy as np
from typing import Dict, List, Tuple

from tests.test_utilities.hla_preparation_utils import create_hla_typing
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.filters.filter_from_config import filter_from_config
from txmatching.optimizer.optimizer_return_object import OptimizerReturn
from txmatching.optimizer.optimizer_request_object import OptimizerRequest, Pair
from txmatching.patients.hla_model import HLAAntibodies
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.patients.patient import Donor, DonorType, Recipient
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solve_service.solve_from_configuration import filter_and_sort_matchings
from txmatching.solve_service.solver_lock import run_with_solver_lock
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver
from txmatching.solvers.solver_from_config import solver_from_configuration
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Solver


def calculate_from_optimizer_safe(optimizer_request_object: OptimizerRequest) -> OptimizerReturn:
    return run_with_solver_lock(lambda: _calculate_from_optimizer_unsafe(optimizer_request_object))


def _calculate_from_optimizer_unsafe(optimizer_request_object: OptimizerRequest) -> OptimizerReturn:
    config_parameters = ConfigParameters(
        # todo add more parameters later according to added keywords
        solver_constructor_name=Solver.ILPSolver,
        max_cycle_length=optimizer_request_object.configuration.limitations.max_cycle_length,
        max_sequence_length=optimizer_request_object.configuration.limitations.max_chain_length
    )

    donors_dict, recipients_dict = _create_patients(optimizer_request_object.pairs)

    scorer = scorer_from_configuration(config_parameters)
    solver = solver_from_configuration(config_parameters,
                                       donors_dict=donors_dict,
                                       recipients_dict=recipients_dict,
                                       scorer=scorer)

    # TODO is this needed?
    solver.score_matrix = _create_score_matrix(donors_dict, recipients_dict,
                                               optimizer_request_object.compatibility_graph)

    donor_to_recipient = {pair.donor_id: pair.recipient_id for pair in optimizer_request_object.pairs}
    data_and_configuration = DataAndConfigurationForILPSolver(donors_dict, recipients_dict, config_parameters)

    comp_matrix = _get_donor_score_matrix(optimizer_request_object.compatibility_graph, donor_to_recipient)

    data_and_configuration.graph = _create_graph(comp_matrix, data_and_configuration.non_directed_donors,
                                                 donor_to_recipient)

    all_matchings = solver.solve(data_and_configuration)

    matching_filter = filter_from_config(config_parameters)

    matchings_filtered_sorted, _, _ = filter_and_sort_matchings(all_matchings, matching_filter, config_parameters)

    print("im here at the end with these matchings", len(matchings_filtered_sorted))
    for matching in matchings_filtered_sorted:
        print("this is a mathcing")
        for pair in matching.matching_pairs:
            print((pair.donor.db_id, pair.recipient.db_id))
    # TODO
    return None


def _create_patients(pairs: List[Pair]) -> Tuple[Dict[int, Donor], Dict[int, Recipient]]:
    donors_dict = {}
    recipients_dict = {}

    for pair in pairs:
        if pair.donor_id not in donors_dict:
            donors_dict[pair.donor_id] = _create_empty_donor(pair)
        if pair.recipient_id is not None and pair.recipient_id not in recipients_dict:
            list_of_donors = [pair.donor_id for inner_pair in pairs if inner_pair.recipient_id == pair.recipient_id]
            recipients_dict[pair.recipient_id] = _create_empty_recipient(pair, list_of_donors)

    return donors_dict, recipients_dict


def _create_empty_donor(pair: Pair) -> Donor:
    return Donor(
        db_id=pair.donor_id,
        medical_id=str(pair.donor_id) + "_DONOR",
        parameters=_create_empty_parameters(),
        etag=1,
        donor_type=DonorType.DONOR if pair.recipient_id else DonorType.NON_DIRECTED,
        related_recipient_db_id=pair.recipient_id if pair.recipient_id else None,
        active=True
    )


def _create_empty_recipient(pair: Pair, list_of_donors: List[int]) -> Recipient:
    return Recipient(
        db_id=pair.recipient_id,
        medical_id=str(pair.recipient_id) + "_RECIPIENT",
        parameters=_create_empty_parameters(),
        etag=1,
        related_donors_db_ids=list_of_donors,
        hla_antibodies=HLAAntibodies([], []),
        acceptable_blood_groups=[],
    )


def _create_empty_parameters():
    # TODO maybe change this to something sensible
    return PatientParameters(
        blood_group=BloodGroup.A,
        country_code=Country.AZE,
        hla_typing=create_hla_typing(['A9', 'B42', 'DR4', 'DQ8']),
    )


def _create_score_matrix(donors_dict: Dict[int, Recipient], recipients_dict: Dict[int, Donor],
                         comp_graph: List[Dict[str, int]]) -> np.array:
    score_matrix = [
        [
            _hla_score_for_pair(donor.db_id, recipient.db_id, comp_graph) for recipient in recipients_dict.values()
        ]
        for donor in donors_dict.values()]

    return np.array(score_matrix)


def _hla_score_for_pair(donor_id: int, recipient_id: int, comp_graph: List[Dict[str, int]]) -> int:
    for row in comp_graph:
        if ("donor_index" in row and "recipient_index" in row and "hla_compatibility_score" in row and row[
            "donor_index"] == donor_id and row["recipient_index"] == recipient_id):
            return row["hla_compatibility_score"]
    return -1


def _create_graph(comp_matrix: np.array, non_directed_donors: List[int],
                  donor_to_recipient: Dict[int, int]) -> nx.Graph:
    num_nodes = len(comp_matrix)
    edges = []
    for from_node in range(0, num_nodes):
        for to_node in range(0, num_nodes):
            weight = int(comp_matrix[from_node][to_node])
            if weight >= 0:
                edges.append((from_node, to_node, weight))
    graph = nx.DiGraph()

    graph.add_nodes_from([
        (node, {'ndd': node in non_directed_donors})
        for node in range(0, len(donor_to_recipient))
    ])

    graph.add_edges_from([
        (from_node, to_node, {'weight': weight})
        for (from_node, to_node, weight) in edges
    ])
    return graph


def _get_donor_score_matrix(comp_graph: List[Dict[str, int]], donor_to_recipient: Dict[int, int]) -> np.array:
    score_matrix = []

    for donor_id, recipient_id in donor_to_recipient.items():
        row = []
        for donor_id_inner, recipient_id_inner in donor_to_recipient.items():
            if recipient_id_inner is not None and donor_id != donor_id_inner and recipient_id != recipient_id_inner:
                row.append(_hla_score_for_pair(donor_id, recipient_id_inner, comp_graph))
            else:
                row.append(-1)
        score_matrix.append(row)

    score_matrix = np.array(score_matrix)

    return score_matrix
