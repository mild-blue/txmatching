import logging
import tempfile
from os import close, dup, dup2
from typing import Iterable, List, Tuple

import mip

from txmatching.auth.exceptions import \
    CannotFindShortEnoughRoundsOrPathsInILPSolver
from txmatching.patients.patient import Donor, Recipient
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
from txmatching.utils.enums import HLACrossmatchLevel

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

    _add_constraints_removing_solution_return_missing_set(ilp_model, data_and_configuration, [], mapping)

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
                    _is_split_crossmatch_and_nothing_high_res(data_and_configuration.configuration.hla_crossmatch_level,
                                                              data_and_configuration.active_and_valid_donors_list,
                                                              data_and_configuration.active_and_valid_recipients_list)
                    _is_majority_of_recipients_missing_antibodies(
                        data_and_configuration.active_and_valid_recipients_list)
                    raise CannotFindShortEnoughRoundsOrPathsInILPSolver

        if status == Status.OPTIMAL:
            solution_edges = [edge for edge, var in mapping.edge_to_var.items() if mip_var_to_bool(var)]
            yield Solution(solution_edges)
            some_solution_yielded = True
            missing = _add_constraints_removing_solution_return_missing_set(ilp_model, data_and_configuration,
                                                                            solution_edges, mapping)
            if missing == set():
                return
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


def _add_constraints_removing_solution_return_missing_set(ilp_model: mip.Model,
                                                          data_and_configuration: DataAndConfigurationForILPSolver,
                                                          solution_edges: Iterable[Tuple[int, int]],
                                                          mapping: VariableMapping
                                                          ) -> set():
    edges_in_alternative_solution = set(data_and_configuration.graph.edges) - set(solution_edges)

    end_of_chain_edges = _find_all_end_of_chain_edges(solution_edges)
    for solution_edge in end_of_chain_edges:
        recipient_at_the_end_of_chain = data_and_configuration.donor_enum_to_related_recipient[solution_edge[1]]
        all_donors_of_recipient = data_and_configuration.recipient_to_donors_enum_dict[
            recipient_at_the_end_of_chain]
        for donor_enum in all_donors_of_recipient:
            edges_in_alternative_solution.discard((solution_edge[0], donor_enum))

    ilp_model.add_constr(mip.xsum([mapping.edge_to_var[edge] for edge in edges_in_alternative_solution]) >= 0.5)
    return edges_in_alternative_solution


def _find_all_end_of_chain_edges(solution_edges: Iterable[Tuple[int, int]]) -> set():
    set_of_donors = set({solution_edge[0] for solution_edge in solution_edges})

    end_of_chain_edges = set(
        {solution_edge for solution_edge in solution_edges if solution_edge[1] not in set_of_donors})

    return end_of_chain_edges


def _is_majority_of_recipients_missing_antibodies(recipient_list: List[Recipient]):
    number_of_recipients = len(recipient_list)
    recipients_without_antibodies = 0
    for recipient in recipient_list:
        hla_antibodies_count = sum([len(hla_antibody_per_group.hla_antibody_list) for hla_antibody_per_group in
                                    recipient.hla_antibodies.hla_antibodies_per_groups])
        if hla_antibodies_count == 0:
            recipients_without_antibodies = recipients_without_antibodies + 1
            if recipients_without_antibodies > number_of_recipients / 2:
                raise CannotFindShortEnoughRoundsOrPathsInILPSolver(
                    "Majority of recipients don't have any antibodies. Check, if this is correct. " +
                    CannotFindShortEnoughRoundsOrPathsInILPSolver.default_message)


def _is_split_crossmatch_and_nothing_high_res(hla_crossmatch_level: HLACrossmatchLevel, donors: List[Donor],
                                              recipients: List[Recipient]):
    if hla_crossmatch_level is HLACrossmatchLevel.SPLIT_AND_BROAD:
        for donor in donors:
            for hla_per_group in donor.parameters.hla_typing.hla_per_groups:
                for hla_type in hla_per_group.hla_types:
                    if hla_type.code.high_res is not None:
                        return
        for recipient in recipients:
            for hla_per_group in recipient.parameters.hla_typing.hla_per_groups:
                for hla_type in hla_per_group.hla_types:
                    if hla_type.code.high_res is not None:
                        return
            for antibodies_per_group in recipient.hla_antibodies.hla_antibodies_per_groups:
                for antibody_per_group in antibodies_per_group.hla_antibody_list:
                    if antibody_per_group.code.high_res is not None:
                        return
        raise CannotFindShortEnoughRoundsOrPathsInILPSolver(
            "Split and broad crossmatch is set, but all the patients have only split or broad resolution. " +
            "Change the allowed crossmatch type to broad, or none.")  # todo
