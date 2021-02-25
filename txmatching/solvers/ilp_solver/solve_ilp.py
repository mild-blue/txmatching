import logging
import tempfile
from os import close, dup, dup2
from typing import Iterable, List, Tuple

import mip

from txmatching.solvers.ilp_solver.generate_dynamic_constraints import \
    add_dynamic_constraints
from txmatching.solvers.ilp_solver.ilp_dataclasses import (
    InternalILPSolverParameters, ObjectiveType, VariableMapping)
from txmatching.solvers.ilp_solver.mip_utils import (mip_get_result_status,
                                                     mip_var_to_bool)
from txmatching.solvers.ilp_solver.solution import Solution, Status
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver

logger = logging.getLogger(__name__)


def solve_ilp(data_and_configuration: DataAndConfigurationForILPSolver,
              internal_parameters: InternalILPSolverParameters = InternalILPSolverParameters()) -> List[Solution]:
    if len(data_and_configuration.graph.edges) < 1:
        return []
    ilp_model = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)
    mapping = VariableMapping(ilp_model, data_and_configuration)

    _add_objective(ilp_model, internal_parameters, data_and_configuration, mapping)

    _add_static_constraints(data_and_configuration, ilp_model, mapping)
    solutions = []
    for _ in range(data_and_configuration.configuration.max_number_of_solutions_for_ilp):
        while True:
            _solve_with_logging(ilp_model)

            status = mip_get_result_status(ilp_model)
            dynamic_constraints_added = add_dynamic_constraints(data_and_configuration,
                                                                internal_parameters,
                                                                ilp_model,
                                                                mapping.edge_to_var)
            if not dynamic_constraints_added:
                break

        if status == Status.Optimal:
            solution_edges = [edge for edge, var in mapping.edge_to_var.items() if mip_var_to_bool(var)]
            solutions.append(Solution(solution_edges))
            _add_constraints_removing_solution(ilp_model, data_and_configuration, solution_edges, mapping)
        else:
            break

    return solutions


def _add_static_constraints(data_and_configuration: DataAndConfigurationForILPSolver,
                            ilp_model: mip.Model,
                            mapping: VariableMapping):
    # Total inflow into node.
    for node in data_and_configuration.graph.nodes():
        ilp_model.add_constr(
            mip.xsum([mapping.edge_to_var[edge] for edge in data_and_configuration.graph.in_edges(node)]) ==
            mapping.node_to_in_var[node])

    # Total outflow from node.
    for node in data_and_configuration.graph.nodes():
        ilp_model.add_constr(
            mip.xsum([mapping.edge_to_var[edge] for edge in data_and_configuration.graph.out_edges(node)]) ==
            mapping.node_to_out_var[node])

    # Donor-patient pair flows.
    for node in data_and_configuration.dp_pairs:
        ilp_model.add_constr(mapping.node_to_out_var[node] <= mapping.node_to_in_var[node])
        ilp_model.add_constr(mapping.node_to_in_var[node] <= 1)

    # Non-directed donor flows.
    for node in data_and_configuration.non_directed_donors:
        ilp_model.add_constr(mapping.node_to_out_var[node] <= 1)


def _add_objective(ilp_model: mip.Model,
                   internal_parameters: InternalILPSolverParameters,
                   data_and_configuration: DataAndConfigurationForILPSolver,
                   mapping: VariableMapping):
    # Objective.
    if internal_parameters.objective_type == ObjectiveType.MaxTransplantsMaxWeights:
        weight_of_addition_of_extra_pair = max([data['weight'] for (_, _, data) in data_and_configuration.graph.edges(
            data=True)]) * data_and_configuration.graph.number_of_nodes()
        ilp_model.objective = mip.xsum([
            (weight_of_addition_of_extra_pair * mapping.edge_to_var[from_node, to_node]) + (
                    data_and_configuration.graph[from_node][to_node]['weight'] * mapping.edge_to_var[
                from_node, to_node])
            for (from_node, to_node) in data_and_configuration.graph.edges()
        ])
    elif internal_parameters.objective_type == ObjectiveType.MaxTransplants:
        ilp_model.objective = mip.xsum([
            mapping.edge_to_var[from_node, to_node]
            for (from_node, to_node) in data_and_configuration.graph.edges()
        ])
    elif internal_parameters.objective_type == ObjectiveType.MaxWeights:
        ilp_model.objective = mip.xsum([
            data_and_configuration.graph[from_node][to_node]['weight'] * mapping.edge_to_var[from_node, to_node]
            for (from_node, to_node) in data_and_configuration.graph.edges()
        ])
    else:
        raise Exception('Unknown objective type.')


def _solve_with_logging(ilp_model: mip.Model):
    with tempfile.TemporaryFile() as tmp_output:
        orig_std_out = dup(1)
        dup2(tmp_output.fileno(), 1)
        ilp_model.optimize()
        dup2(orig_std_out, 1)
        close(orig_std_out)
        if logging.DEBUG >= logging.root.level:
            tmp_output.seek(0)
            for line in tmp_output.read().splitlines():
                logger.debug(line.decode('utf8'))


def _add_constraints_removing_solution(ilp_model: mip.Model,
                                       data_and_configuration: DataAndConfigurationForILPSolver,
                                       solution_edges: Iterable[Tuple[int, int]],
                                       mapping: VariableMapping
                                       ):
    sol_edges_set = set(solution_edges)
    missing = {(from_node, to_node) for (from_node, to_node) in data_and_configuration.graph.edges if
               (from_node, to_node) not in sol_edges_set}

    ilp_model.add_constr(mip.xsum([mapping.edge_to_var[edge] for edge in missing]) >= 0.5)
