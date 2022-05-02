import itertools
import logging
import tempfile
from os import close, dup, dup2
from typing import Iterable, List, Tuple

import mip

from txmatching.auth.exceptions import \
    CannotFindShortEnoughRoundsOrPathsInILPSolver
from txmatching.solvers.ilp_solver.generate_dynamic_constraints import \
    add_dynamic_constraints
from txmatching.solvers.ilp_solver.ilp_dataclasses import (
    InternalILPSolverParameters, ObjectiveType, VariableMapping)
from txmatching.solvers.ilp_solver.mip_utils import (mip_get_result_status,
                                                     mip_var_to_bool)
from txmatching.solvers.ilp_solver.solution import Solution, Status
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver
from txmatching.utils.blood_groups import BloodGroup

logger = logging.getLogger(__name__)


def solve_ilp(data_and_configuration: DataAndConfigurationForILPSolver,
              internal_parameters: InternalILPSolverParameters = InternalILPSolverParameters()) -> Iterable[Solution]:
    if len(data_and_configuration.graph.edges) < 1:
        return
    ilp_model = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)
    mapping = VariableMapping(ilp_model, data_and_configuration)

    _add_objective(ilp_model, internal_parameters, data_and_configuration, mapping)

    _add_static_constraints(data_and_configuration, ilp_model, mapping)

    matchings_to_search_for = min(data_and_configuration.configuration.max_number_of_matchings,
                                  data_and_configuration.configuration.max_matchings_in_ilp_solver)
    some_solution_yielded = False

    _add_constraints_removing_solution(ilp_model, data_and_configuration, [], mapping)

    for _ in range(matchings_to_search_for):
        number_of_times_dynamic_constraint_added = 0
        while True:
            _solve_with_logging(ilp_model)

            status = mip_get_result_status(ilp_model)
            dynamic_constraints_added = add_dynamic_constraints(data_and_configuration,
                                                                internal_parameters,
                                                                ilp_model,
                                                                mapping.edge_to_var)
            if not dynamic_constraints_added:
                break
            number_of_times_dynamic_constraint_added += 1
            if number_of_times_dynamic_constraint_added > \
                    data_and_configuration.configuration.max_number_of_dynamic_constrains_ilp_solver:
                if not some_solution_yielded:
                    raise CannotFindShortEnoughRoundsOrPathsInILPSolver(
                        'Unable to find solution complying with required length of cycles and sequences.'
                        f'Number of added dynamic constraints reached a threshold of'
                        f' {data_and_configuration.configuration.max_number_of_dynamic_constrains_ilp_solver}')
        if status == Status.OPTIMAL:
            solution_edges = [edge for edge, var in mapping.edge_to_var.items() if mip_var_to_bool(var)]
            yield Solution(solution_edges)
            some_solution_yielded = True

            if (data_and_configuration.graph.edges - set(solution_edges)) == set():
                break
            _add_constraints_removing_solution(ilp_model, data_and_configuration, solution_edges, mapping)
        else:
            break


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

    # Total outflow and inflow of one recipient should be at most 1.
    for donors_node_ids in data_and_configuration.recipient_to_donors_enum_dict.values():
        ilp_model.add_constr(mip.xsum([mapping.node_to_in_var[node] for node in donors_node_ids]) <= 1)

    # Donor-patient pair flows.
    for node in data_and_configuration.regular_donors:
        ilp_model.add_constr(mapping.node_to_out_var[node] <= mapping.node_to_in_var[node])
        ilp_model.add_constr(mapping.node_to_in_var[node] <= 1)

    # Non-directed donor flows.
    for node in data_and_configuration.non_directed_donors:
        ilp_model.add_constr(mapping.node_to_out_var[node] <= 1)

    # Required patients
    for node in data_and_configuration.required_patients:
        ilp_model.add_constr(mapping.node_to_in_var[node] >= 0.5)

    add_debt_static_constraints(ilp_model, data_and_configuration, mapping)

    add_blood_group_zero_debt_static_constraints(ilp_model, data_and_configuration, mapping)


def add_debt_static_constraints(ilp_model,
                                data_and_configuration: DataAndConfigurationForILPSolver,
                                mapping: VariableMapping):
    countries = set(data_and_configuration.country_codes_dict.values())
    for current_country in countries:
        country_giving = [mapping.node_to_out_var[node] for node, country in
                          data_and_configuration.country_codes_dict.items() if country == current_country]
        country_receiving = [- mapping.node_to_in_var[node] for node, country in
                             data_and_configuration.country_codes_dict.items() if country == current_country]

        ilp_model.add_constr(
            mip.xsum(country_giving + country_receiving) <= data_and_configuration.configuration.max_debt_for_country)
        ilp_model.add_constr(
            - mip.xsum(country_giving + country_receiving) <= data_and_configuration.configuration.max_debt_for_country)


def add_blood_group_zero_debt_static_constraints(ilp_model,
                                                 data_and_configuration: DataAndConfigurationForILPSolver,
                                                 mapping: VariableMapping):
    countries = set(data_and_configuration.country_codes_dict.values())

    for current_country in countries:

        country_giving = [mapping.node_to_out_var[node] for node, country in
                          data_and_configuration.country_codes_dict.items() if country == current_country and
                          data_and_configuration.blood_groups_dict[node] == BloodGroup.ZERO]
        country_receiving = []
        nodes_of_current_country = [node for node, country in data_and_configuration.country_codes_dict.items() if
                                    country == current_country]
        nodes_of_other_countries_with_blood_group_zero = [node for node, country in
                                                          data_and_configuration.country_codes_dict.items() if
                                                          data_and_configuration.blood_groups_dict[
                                                              node] == BloodGroup.ZERO]
        for current_country_node in nodes_of_current_country:
            for other_country_node in nodes_of_other_countries_with_blood_group_zero:
                maybe_edge_to_var = mapping.edge_to_var.get((other_country_node, current_country_node))
                if maybe_edge_to_var is not None:
                    country_receiving.append(- maybe_edge_to_var)
        constraint = data_and_configuration.configuration.max_debt_for_country_for_blood_group_zero
        ilp_model.add_constr(mip.xsum(country_giving + country_receiving) <= constraint)
        ilp_model.add_constr(- mip.xsum(country_giving + country_receiving) <= constraint)


def _add_objective(ilp_model: mip.Model,
                   internal_parameters: InternalILPSolverParameters,
                   data_and_configuration: DataAndConfigurationForILPSolver,
                   mapping: VariableMapping):
    # Objective.
    if internal_parameters.objective_type == ObjectiveType.MAX_TRANSPLANTS_MAX_WEIGHTS:
        weight_of_addition_of_extra_pair = max([data['weight'] for (_, _, data) in data_and_configuration.graph.edges(
            data=True)]) * data_and_configuration.graph.number_of_nodes()
        ilp_model.objective = mip.xsum([
            (weight_of_addition_of_extra_pair * mapping.edge_to_var[from_node, to_node]) + (
                    data_and_configuration.graph[from_node][to_node]['weight'] * mapping.edge_to_var[
                from_node, to_node])
            for (from_node, to_node) in data_and_configuration.graph.edges()
        ])
    elif internal_parameters.objective_type == ObjectiveType.MAX_TRANSPLANTS:
        ilp_model.objective = mip.xsum([
            mapping.edge_to_var[from_node, to_node]
            for (from_node, to_node) in data_and_configuration.graph.edges()
        ])
    elif internal_parameters.objective_type == ObjectiveType.MAX_WEIGHTS:
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
    # convert solution_edges from donor-to-donor to recipient-to-recipient (-1 means no recipient)
    recipient_to_recipient_solution_edges = set()
    # remember all donoring counterparts expressed as their recipients
    donoring_counterpart_ids = {}
    for donor_to_recipient in solution_edges:
        # if the donor is non-directed, it evaluates to -1
        if data_and_configuration.donor_to_recipient_related[
            data_and_configuration.donor_enum_to_id[donor_to_recipient[0]]] is not None:
            recipient_of_donating_donor = data_and_configuration.donor_to_recipient_related[
                data_and_configuration.donor_enum_to_id[donor_to_recipient[0]]]
            donoring_counterpart_ids[recipient_of_donating_donor] = 1
        else:
            recipient_of_donating_donor = -1
        # bridging donors
        if data_and_configuration.donor_to_recipient_related[
            data_and_configuration.donor_enum_to_id[donor_to_recipient[1]]] is not None:
            recipient_of_recieving_donor = data_and_configuration.donor_to_recipient_related[
                data_and_configuration.donor_enum_to_id[donor_to_recipient[1]]]
        else:
            recipient_of_recieving_donor = -2
        recipient_to_recipient_solution_edges.add((recipient_of_donating_donor, recipient_of_recieving_donor))

    # note all the donors at the end of the chain to be excluded (there might be several chains)
    donors_to_exclude = []
    for recipient_to_recipient in recipient_to_recipient_solution_edges:
        if recipient_to_recipient[1] not in donoring_counterpart_ids and len(
                data_and_configuration.recipient_to_donors_enum_dict[recipient_to_recipient[1]]) > 1:
            donors_to_exclude.append(data_and_configuration.recipient_to_donors_enum_dict[recipient_to_recipient[1]])

    # if there are no additional donors to exclude, exclude only one solution edges set and return
    if len(donors_to_exclude) == 0:
        sol_edges_set = set(solution_edges)
        missing = {(from_node, to_node) for (from_node, to_node) in data_and_configuration.graph.edges if
                   (from_node, to_node) not in sol_edges_set}
        ilp_model.add_constr(mip.xsum([mapping.edge_to_var[edge] for edge in missing]) >= 0.5)
        return

    # create all possible combinations to exclude and exclude them
    solution_edges_list = list(solution_edges)
    permutations = list(itertools.product(*donors_to_exclude))
    for permutation in permutations:
        value_to_index_dict = {}
        for index, donor_list in enumerate(donors_to_exclude):
            for donor in donor_list:
                value_to_index_dict[donor] = index

        for index, solution_edge in enumerate(solution_edges_list):
            if solution_edge[1] in value_to_index_dict:
                solution_edges_list[index] = (solution_edge[0], permutation[value_to_index_dict[solution_edge[1]]])

        sol_edges_set = set(solution_edges_list)
        missing = {(from_node, to_node) for (from_node, to_node) in data_and_configuration.graph.edges if
                   (from_node, to_node) not in sol_edges_set}
        ilp_model.add_constr(mip.xsum([mapping.edge_to_var[edge] for edge in missing]) >= 0.5)
