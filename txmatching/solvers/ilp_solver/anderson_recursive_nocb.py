# pylint: skip-file
# TODO: improve the code https://github.com/mild-blue/txmatching/issues/430
from enum import IntEnum
from typing import Dict, Tuple

import mip
import networkx as nx

from txmatching.solvers.ilp_solver.mip_utils import (mip_get_result_status,
                                                     mip_var_to_bool)
from txmatching.solvers.ilp_solver.result import Result
from txmatching.solvers.ilp_solver.solution import Solution, Status
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    TXMConfigurationForILPSolver


#
class MaxSequenceLimitMethod(IntEnum):
    LazyForbidAllMaximalSequences = 0
    '''Lazy constraints. Forbid all maximal sequences that are larger than the limit.'''

    LazyForbidSmallestMaximalSequence = 1
    '''Lazy constraints. Forbid smallest maximal sequences that is larger than the limit.'''

    # LazyForbidAllSubsequences = 2
    '''Lazy constraints. Forbid all subsequences that are larger than the limit.'''


class ObjectiveType(IntEnum):
    MaxTransplants = 0
    '''Maximize the number of transplants.'''

    MaxWeights = 1
    '''Maximize the total transplants weights.'''

    MaxTransplantsMaxWeights = 2
    '''Maximize the number of transplants and then maximize their total weight.'''


class SolverConfig:

    def __init__(
            self,
            objective_type: ObjectiveType,
            max_sequence_limit_method: MaxSequenceLimitMethod = MaxSequenceLimitMethod.LazyForbidAllMaximalSequences):
        self.objective_type = objective_type
        self.max_sequence_limit_method = max_sequence_limit_method


def generate_constrs(ins: TXMConfigurationForILPSolver, cfg: SolverConfig, m: mip.Model,
                     y: Dict[Tuple[int, int], mip.Var]):
    yval = {key: mip_var_to_bool(var) for key, var in y.items()}

    sol_graph = nx.DiGraph()
    sol_graph.add_edges_from([edge for edge, val in yval.items() if val])

    # 1. Create a graph only from the edges of the solution.
    # 2. Split the graph into weakly connected components
    # 3. Split the components to cycles and sequences (in correctly constructed model, each component is either a
    #  cycle or sequence).
    #
    # Components with isolated nodes are considered to be sequences.
    comps = list(nx.weakly_connected_components(sol_graph))
    cycles = []
    seqs = []

    # Split components to sequences and cycles.
    for comp in comps:
        comp = list(comp)
        try:
            cycle = nx.find_cycle(sol_graph, source=comp[0])
            cycles.append(cycle)
        except nx.NetworkXNoCycle:
            seqs.append(sol_graph.edges(comp))

    cons_added = False

    # Limiting max cycle length.
    # The cycle detection in each cycle component can start from any node (due to the
    # assumed shape of the components).
    # TODO: currently forbids all invalid cycles.
    # TODO: config for which cycles to forbid
    cycles_to_forbid = []
    for cycle in cycles:
        if len(cycle) > ins.max_cycle_length:
            cycles_to_forbid.append(cycle)
    for cycle in cycles_to_forbid:
        m.add_constr(mip.xsum([y[edge] for edge in cycle]) <= len(cycle) - 1)
        cons_added = True

    # Limiting max cycle length.
    violating_seqs = [seq for seq in seqs if len(seq) > ins.max_sequence_length]
    if violating_seqs:
        seqs_to_forbid = []
        if cfg.max_sequence_limit_method == MaxSequenceLimitMethod.LazyForbidAllMaximalSequences:
            seqs_to_forbid.extend(violating_seqs)
        elif cfg.max_sequence_limit_method == MaxSequenceLimitMethod.LazyForbidSmallestMaximalSequence:
            seqs_to_forbid.append(min(violating_seqs, key=lambda seq: len(seq)))

        for seq in seqs_to_forbid:
            m.add_constr(mip.xsum([y[edge] for edge in seq]) <= len(seq) - 1)
            cons_added = True

    return cons_added


def solve_ilp(ins: TXMConfigurationForILPSolver, cfg: SolverConfig) -> Result:
    if len(ins.graph.edges) < 1:
        return Result(
            status=Status.NoSolution
        )
    m = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)

    # Mapping from edge e to variable y_e
    y = dict()
    for (from_node, to_node) in ins.graph.edges():
        y[from_node, to_node] = m.add_var(var_type=mip.BINARY, name=f'y[{from_node},{to_node}]')

    # Mapping from node v to variable f^i_v
    fi = dict()
    for node in ins.graph.nodes():
        fi[node] = m.add_var(lb=0, var_type=mip.INTEGER, name=f'fi[{node}]')

    # Mapping from node v to variable f^o_v
    fo = dict()
    for node in ins.graph.nodes():
        fo[node] = m.add_var(lb=0, var_type=mip.INTEGER, name=f'fi[{node}]')

    # Objective.
    if cfg.objective_type == ObjectiveType.MaxTransplantsMaxWeights:
        max_weight = max([data['weight'] for (_, _, data) in ins.graph.edges(data=True)]) * ins.graph.number_of_nodes()
        m.objective = mip.xsum([
            (max_weight * y[from_node, to_node]) + (ins.graph[from_node][to_node]['weight'] * y[from_node, to_node])
            for (from_node, to_node) in ins.graph.edges()
        ])
    elif cfg.objective_type == ObjectiveType.MaxTransplants:
        m.objective = mip.xsum([
            y[from_node, to_node]
            for (from_node, to_node) in ins.graph.edges()
        ])
    elif cfg.objective_type == ObjectiveType.MaxWeights:
        m.objective = mip.xsum([
            ins.graph[from_node][to_node]['weight'] * y[from_node, to_node]
            for (from_node, to_node) in ins.graph.edges()
        ])
    else:
        raise Exception('Unknown objective type.')

    # Total inflow into node.
    for node in ins.graph.nodes():
        m.add_constr(mip.xsum([y[edge] for edge in ins.graph.in_edges(node)]) == fi[node])

    # Total outflow from node.
    for node in ins.graph.nodes():
        m.add_constr(mip.xsum([y[edge] for edge in ins.graph.out_edges(node)]) == fo[node])

    # Donor-patient pair flows.
    for node in ins.dp_pairs:
        m.add_constr(fo[node] <= fi[node])
        m.add_constr(fi[node] <= 1)

    # Non-directed donor flows.
    for node in ins.non_directed_donors:
        m.add_constr(fo[node] <= 1)

    reoptimize = True
    while reoptimize:
        m.optimize()
        status = mip_get_result_status(m)
        reoptimize = generate_constrs(ins, cfg, m, y)

    solution = None
    if status in (Status.Optimal, Status.Heuristic):
        solution_edges = [edge for edge, var in y.items() if mip_var_to_bool(var)]
        solution = Solution(solution_edges)

    return Result(
        status=status,
        solution=solution)
