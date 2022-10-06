from typing import Dict, List, Tuple

import networkx as nx
import numpy as np

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.optimizer.optimizer_return_object import CycleOrChain, DonorToRecipient, OptimizerReturn, Statistics
from txmatching.optimizer.optimizer_request_object import Limitations, OptimizerConfiguration, OptimizerRequest, Pair
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.patients.patient import Donor, Recipient
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.scorers.split_hla_additive_scorer import SplitScorer
from txmatching.solve_service.solver_lock import run_with_solver_lock
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver
from txmatching.solvers.solver_from_config import solver_from_configuration
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Solver


def calculate_from_optimizer_safe(optimizer_request_object: OptimizerRequest) -> OptimizerReturn:
    return run_with_solver_lock(lambda: _calculate_from_optimizer_unsafe(optimizer_request_object))


# pylint: disable=too-many-locals
def _calculate_from_optimizer_unsafe(optimizer_request_object: OptimizerRequest) -> OptimizerReturn:
    config_parameters = ConfigParameters(
        # todo add more parameters later according to added keywords
        solver_constructor_name=Solver.ILPSolver,
        max_cycle_length=optimizer_request_object.configuration.limitations.max_cycle_length,
        max_sequence_length=optimizer_request_object.configuration.limitations.max_chain_length,
        max_number_of_matchings=1
    )

    scorer = scorer_from_configuration(config_parameters)
    solver = solver_from_configuration(config_parameters,
                                       donors_dict={},
                                       recipients_dict={},
                                       scorer=scorer)
    data_and_configuration = _create_data_and_config_for_ilp(optimizer_request_object.pairs, config_parameters,
                                                             optimizer_request_object.compatibility_graph)
    all_matchings = solver.solve_kepsoft(data_and_configuration)

    if len(all_matchings) == 0:
        return OptimizerReturn(cycles_and_chains=[], statistics=Statistics(0, 0))

    best_matching = all_matchings[0]

    enum_cycles, enum_chains = _get_cycles_and_chains(best_matching)
    cycles, chains = _get_cycles_and_chains_original_ids(enum_cycles, enum_chains, optimizer_request_object.pairs)

    cycles_and_chains = []

    for cycle_or_chain in cycles + chains:
        patients = _get_patients_for_cycle_or_chain(cycle_or_chain, optimizer_request_object.compatibility_graph)
        scores = _get_scores(patients)
        cycle_object = CycleOrChain(
            patients=patients,
            scores=scores
        )
        cycles_and_chains.append(cycle_object)

    statistics = _get_statistics(best_matching, cycles, chains)
    return OptimizerReturn(
        cycles_and_chains=cycles_and_chains,
        statistics=statistics
    )


def _get_cycles_and_chains_original_ids(enum_cycles: List[Tuple[int, int]], enum_chains: List[Tuple[int, int]],
                                        pairs: List[Pair]) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    donor_id_to_enum = {pair.donor_id: i for i, pair in enumerate(pairs)}
    donor_enum_to_id = {i: pair.donor_id for i, pair in enumerate(pairs)}
    donor_enum_to_recipient_id = {donor_id_to_enum[pair.donor_id]: pair.recipient_id for pair in pairs}

    cycles = [[(donor_enum_to_id[pair[0]], donor_enum_to_recipient_id[pair[1]]) for pair in enum_cycle] for enum_cycle
              in enum_cycles]
    chains = [[(donor_enum_to_id[pair[0]], donor_enum_to_recipient_id[pair[1]]) for pair in enum_chain] for enum_chain
              in enum_chains]

    return cycles, chains


# pylint: disable=too-many-branches
def _get_cycles_and_chains(best_matching: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    biggest_index = -1
    for d_to_r in best_matching:
        max_index = max(d_to_r[0], d_to_r[1])
        if max_index > biggest_index:
            biggest_index = max_index
    if biggest_index == -1:
        return [], []

    index_array = [-1] * (biggest_index + 1)
    for d_to_r in best_matching:
        index_array[d_to_r[0]] = d_to_r[1]

    cycles = []
    chains = []

    in_degrees = [0] * (biggest_index + 1)
    for d_to_r in best_matching:
        in_degrees[d_to_r[1]] += 1

    ordered_indexes = []
    for index, item in enumerate(in_degrees):
        if item == 1:
            ordered_indexes.append(index)
        else:
            ordered_indexes.insert(0, index)

    for index in ordered_indexes:
        cycle_or_chain = []
        current = index
        if index_array[current] != -1:
            while True:
                cycle_or_chain.append((current, index_array[current]))
                current_temp = current
                current, index_array[current_temp] = index_array[current], -1

                if index_array[current] == -1 or current < 0 or current > max_index:
                    chains.append(cycle_or_chain)
                    break
                if len(cycle_or_chain) > 0 and index_array[current] == cycle_or_chain[0][0]:
                    cycle_or_chain.append((current, index_array[current]))
                    index_array[current] = -1
                    cycles.append(cycle_or_chain)
                    break

    return cycles, chains


def _get_statistics(best_matching: List[Tuple[int, int]], cycles: List[Tuple[int, int]],
                    chains: List[Tuple[int, int]]) -> Statistics:
    return Statistics(
        number_of_found_cycles_and_chains=len(cycles) + len(chains),
        number_of_found_transplants=len(best_matching)
    )


def _create_data_and_config_for_ilp(pairs: List[Pair], config_parameters: ConfigParameters,
                                    comp_graph: List[Dict[str, int]]) -> DataAndConfigurationForILPSolver:
    data_and_configuration = DataAndConfigurationForILPSolver(
        {}, {}, config_parameters
    )

    donor_id_to_enum = {pair.donor_id: i for i, pair in enumerate(pairs)}
    donor_to_recipient = {pair.donor_id: pair.recipient_id for pair in pairs}
    recipient_ids = [pair.recipient_id for pair in pairs]

    data_and_configuration.non_directed_donors = [i for i, pair in enumerate(pairs) if not pair.recipient_id]
    data_and_configuration.regular_donors = [i for i, pair in enumerate(pairs) if pair.recipient_id is not None]
    data_and_configuration.recipient_to_donors_enum_dict = {}
    for recipient_id in recipient_ids:
        if recipient_id:
            donors_list = [donor_id_to_enum[donor_id_in_dict] for donor_id_in_dict, recipient_id_in_dict in
                           donor_to_recipient.items() if recipient_id_in_dict == recipient_id]
            data_and_configuration.recipient_to_donors_enum_dict[recipient_id] = donors_list
    data_and_configuration.donor_enum_to_related_recipient = {donor_id_to_enum[pair.donor_id]: pair.recipient_id for
                                                              pair in pairs}

    data_and_configuration.country_codes_dict = {i: pairs[i].category for i in range(len(pairs))}

    # we dont really need bloodgroups as an info but we need it for ILP
    data_and_configuration.blood_groups_dict = {i: BloodGroup.A for i in range(len(pairs))}

    comp_matrix = _get_donor_score_matrix(comp_graph, donor_to_recipient)
    data_and_configuration.graph = _create_graph(comp_matrix, data_and_configuration.non_directed_donors,
                                                 donor_to_recipient)

    return data_and_configuration


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


def _hla_score_for_pair(donor_id: int, recipient_id: int, comp_graph: List[Dict[str, int]]) -> int:
    for row in comp_graph:
        if ("donor_id" in row and "recipient_id" in row and "hla_compatibility_score" in row and row[
            "donor_id"] == donor_id and row["recipient_id"] == recipient_id):
            return row["hla_compatibility_score"]
    return -1


def _get_scores(patient_pairs: List[DonorToRecipient]) -> List[int]:
    scores = np.array([pair.score for pair in patient_pairs])
    return np.sum(scores, axis=0).tolist()


def _get_patients_for_cycle_or_chain(cycle_or_chain: List[Tuple[int, int]], comp_graph: List[Dict[str, int]]) -> List[
    DonorToRecipient]:
    return [
        DonorToRecipient(
            pair[0],
            pair[1],
            [_hla_score_for_pair(pair[0], pair[1], comp_graph)]
        ) for pair in cycle_or_chain
    ]


def get_pairs_from_txm_event(donors: Dict[DonorDbId, Donor]) -> List[Pair]:
    pairs = [Pair(donor_id=donor_id, recipient_id=donor.related_recipient_db_id,
                  category=donor.parameters.country_code.value) for donor_id, donor in donors.items()]
    return pairs


def get_optimizer_configuration(config: ConfigParameters) -> OptimizerConfiguration:
    limitations = Limitations(
        max_cycle_length=config.max_cycle_length,
        max_chain_length=config.max_sequence_length,
        custom_algorithm_settings={}
    )
    scoring = [[{"hla_compatibility_score": 1}]]
    return OptimizerConfiguration(
        limitations=limitations,
        scoring=scoring
    )


def get_compatibility_graph_for_optimizer_api(donors_dict: Dict[DonorDbId, Donor],
                                      recipients_dict: Dict[RecipientDbId, Recipient]) -> List[Dict[str, int]]:
    scorer = SplitScorer()

    compatibility_graph_from_scorer = scorer.get_compatibility_graph(recipients_dict, donors_dict)

    compatibility_graph = []
    for i, donor_id in enumerate(donors_dict):
        for j, recipient_id in enumerate(recipients_dict):
            if (i, j) in compatibility_graph_from_scorer:
                comp_graph_cell = {
                    "donor_id": donor_id,
                    "recipient_id": recipient_id,
                    "hla_compatibility_score": int(compatibility_graph_from_scorer[(i, j)])
                }
                compatibility_graph.append(comp_graph_cell)
    return compatibility_graph
