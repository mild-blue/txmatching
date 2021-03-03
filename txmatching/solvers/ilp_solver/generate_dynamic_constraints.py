from typing import Dict, List, Tuple

import mip
import networkx as nx
import numpy as np

from txmatching.solvers.ilp_solver.ilp_dataclasses import (
    InternalILPSolverParameters, MaxSequenceLimitMethod)
from txmatching.solvers.ilp_solver.mip_utils import mip_var_to_bool
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver


def add_dynamic_constraints(data_and_configuration: DataAndConfigurationForILPSolver,
                            internal_configuration: InternalILPSolverParameters,
                            ilp_model: mip.Model,
                            edge_to_var: Dict[Tuple[int, int], mip.Var]):
    edges_in_solution = [edge_nodes for edge_nodes, edge_present in edge_to_var.items()
                         if mip_var_to_bool(edge_present)]

    sol_graph = nx.DiGraph()
    sol_graph.add_edges_from([edge for edge in edges_in_solution])

    cycles = []
    sequences = []

    # Split components to sequences and cycles.
    for component in nx.weakly_connected_components(sol_graph):
        component = list(component)
        try:
            cycle = nx.find_cycle(sol_graph, source=component[0])
            cycles.append(cycle)
        except nx.NetworkXNoCycle:
            # Components with isolated nodes are considered to be sequences.
            sequences.append(sol_graph.edges(component))

    constraints_added = False

    for cycle in _get_cycles_to_forbid(cycles, data_and_configuration):
        ilp_model.add_constr(mip.xsum([edge_to_var[edge] for edge in cycle]) <= len(cycle) - 1)
        constraints_added = True

    for seq in _get_sequences_to_forbid(sequences,
                                        data_and_configuration,
                                        internal_configuration):
        ilp_model.add_constr(mip.xsum([edge_to_var[edge] for edge in seq]) <= len(seq) - 1)
        constraints_added = True

    if not constraints_added:
        if _is_debt_too_big(edges_in_solution, data_and_configuration):
            ilp_model.add_constr(
                mip.xsum([edge_to_var[edge] for edge in edges_in_solution]) <= len(edges_in_solution) - 1)
            constraints_added = True

    return constraints_added


def _too_many_countries(cycle, data_and_configuration: DataAndConfigurationForILPSolver) -> int:
    return len({data_and_configuration.country_codes_dict[i] for edge in cycle for i in
                edge}) > data_and_configuration.configuration.max_number_of_distinct_countries_in_round


def _is_debt_too_big(edges_in_solution, data_and_configuration: DataAndConfigurationForILPSolver):
    countries = set(data_and_configuration.country_codes_dict.values())
    debt_dict = dict()
    for country in countries:
        debt_dict[country] = 0
    for edge_nodes in edges_in_solution:
        debt_dict[data_and_configuration.country_codes_dict[edge_nodes[0]]] += 1
        debt_dict[data_and_configuration.country_codes_dict[edge_nodes[1]]] -= 1
    for country, debt in debt_dict.items():
        if np.abs(debt) > data_and_configuration.configuration.max_debt_for_country:
            return True
    return False


def _get_cycles_to_forbid(cycles, data_and_configuration: DataAndConfigurationForILPSolver) -> List[Tuple[int, int]]:
    # The cycle detection in each cycle component can start from any node (due to the
    # assumed shape of the components).
    # TODO: currently forbids all invalid cycles.
    # TODO: config for which cycles to forbid
    cycles_to_forbid = []
    for cycle in cycles:
        too_many_transplations = len(cycle) > data_and_configuration.configuration.max_cycle_length
        if too_many_transplations or _too_many_countries(cycle, data_and_configuration):
            cycles_to_forbid.append(cycle)

    return cycles_to_forbid


def _get_sequences_to_forbid(sequences, data_and_configuration: DataAndConfigurationForILPSolver,
                             internal_configuration: InternalILPSolverParameters) -> List[Tuple[int, int]]:
    non_compliant_sequences = []
    for sequence in sequences:
        too_many_transplations = len(sequence) > data_and_configuration.configuration.max_sequence_length
        if too_many_transplations or _too_many_countries(sequence, data_and_configuration):
            non_compliant_sequences.append(sequence)

    sequences_to_forbid = []
    if non_compliant_sequences:

        if internal_configuration.max_sequence_limit_method == MaxSequenceLimitMethod.LazyForbidAllMaximalSequences:
            sequences_to_forbid.extend(non_compliant_sequences)
        elif internal_configuration.max_sequence_limit_method == \
                MaxSequenceLimitMethod.LazyForbidSmallestMaximalSequence:
            sequences_to_forbid.append(min(non_compliant_sequences, key=len))
    return sequences_to_forbid
