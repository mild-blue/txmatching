from typing import Dict, Tuple

import mip
import networkx as nx

from txmatching.solvers.ilp_solver.ilp_dataclasses import (
    InternalILPSolverParameters, MaxSequenceLimitMethod)
from txmatching.solvers.ilp_solver.mip_utils import mip_var_to_bool
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver


# pylint: disable=too-many-locals
def add_dynamic_constraints(data_and_configuration: DataAndConfigurationForILPSolver,
                            internal_configuration: InternalILPSolverParameters,
                            ilp_model: mip.Model,
                            edge_to_var: Dict[Tuple[int, int], mip.Var]):
    edges_in_solution = {edge_nodes: mip_var_to_bool(edge_present) for edge_nodes, edge_present in edge_to_var.items()}

    sol_graph = nx.DiGraph()
    sol_graph.add_edges_from([edge for edge, is_edge in edges_in_solution.items() if is_edge])

    comps = list(nx.weakly_connected_components(sol_graph))
    cycles = []
    sequences = []

    # Split components to sequences and cycles.
    for comp in comps:
        comp = list(comp)
        try:
            cycle = nx.find_cycle(sol_graph, source=comp[0])
            cycles.append(cycle)
        except nx.NetworkXNoCycle:
            # Components with isolated nodes are considered to be sequences.
            sequences.append(sol_graph.edges(comp))

    cons_added = False

    # Limiting max cycle length.
    # The cycle detection in each cycle component can start from any node (due to the
    # assumed shape of the components).
    # TODO: currently forbids all invalid cycles.
    # TODO: config for which cycles to forbid
    cycles_to_forbid = []
    for cycle in cycles:
        too_many_transplations = len(cycle) > data_and_configuration.configuration.max_cycle_length
        if too_many_transplations or _too_many_countries(cycle, data_and_configuration):
            cycles_to_forbid.append(cycle)
    for cycle in cycles_to_forbid:
        ilp_model.add_constr(mip.xsum([edge_to_var[edge] for edge in cycle]) <= len(cycle) - 1)
        cons_added = True

    # Limiting max sequence length.
    non_compliant_sequences = []
    for sequence in sequences:
        too_many_transplations = len(sequence) > data_and_configuration.configuration.max_sequence_length
        if too_many_transplations or _too_many_countries(sequence, data_and_configuration):
            non_compliant_sequences.append(sequence)

    if non_compliant_sequences:
        sequences_to_forbid = []
        if internal_configuration.max_sequence_limit_method == MaxSequenceLimitMethod.LazyForbidAllMaximalSequences:
            sequences_to_forbid.extend(non_compliant_sequences)
        elif internal_configuration.max_sequence_limit_method == \
                MaxSequenceLimitMethod.LazyForbidSmallestMaximalSequence:
            sequences_to_forbid.append(min(non_compliant_sequences, key=len))

        for seq in sequences_to_forbid:
            ilp_model.add_constr(mip.xsum([edge_to_var[edge] for edge in seq]) <= len(seq) - 1)
            cons_added = True

    return cons_added


def _too_many_countries(cycle, data_and_configuration) -> int:
    return len({data_and_configuration.country_codes_dict[i] for edge in cycle for i in
                edge}) > data_and_configuration.configuration.max_number_of_distinct_countries_in_round
