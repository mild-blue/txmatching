import logging
from typing import Dict, List, Set

import mip
from mip import ConstraintPriority, Var

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.solvers.all_solutions_solver.compatibility_graph_utils import \
    PathWithScore
from txmatching.solvers.ilp_solver.mip_utils import (mip_get_result_status,
                                                     mip_var_to_bool,
                                                     solve_with_logging)
from txmatching.solvers.ilp_solver.solution import Status

logger = logging.getLogger(__name__)


# pylint:disable=too-many-locals
def optimise_paths(paths_ids_with_the_same_donors: Dict[int, List[int]],
                   path_id_to_path_with_score: Dict[int, PathWithScore],
                   config: ConfigParameters,
                   required_paths_per_recipient: List[List[int]]):
    """Build and solve the lexicographic optimisation integer programming model.

    Parameters:
    ntpo -- number of possible cycles/chains
    incomp -- list containing the incompatibilities between cycles/chains
    weights -- weights of the cycles/chains according to the criteria given in lexicographic order
    """

    # model
    ilp_model = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)
    path_id_to_var = {}
    for path_id in path_id_to_path_with_score:
        path_id_to_var[path_id] = ilp_model.add_var(var_type=mip.BINARY, name=f'path_id {path_id}')

    max_score = max(path_info.score for path_info in path_id_to_path_with_score.values())
    donor_count = len({donor_id for path in path_id_to_path_with_score.values() for donor_id in path.donor_ids})
    # This multiplicator of number of donors in path ensures that we prioritize first number of donors in the cycle
    # and only second the overall score. In the future this will be changed to include multiple criterions
    # and then probably better solution will be to iteratively find optimality for first objective,
    # then fix the value of the first and optimize the second. But this works well for the moment.
    number_of_transplants_multiplier = max_score * donor_count + 1
    ilp_model.objective = mip.xsum(
        var * (path_id_to_path_with_score[path_id].score +
               number_of_transplants_multiplier * path_id_to_path_with_score[path_id].length)
        for path_id, var in path_id_to_var.items()
    )

    for donor_id, path_ids in paths_ids_with_the_same_donors.items():
        ilp_model.add_constr(
            mip.xsum([path_id_to_var[path_id] for path_id in path_ids]) <= 1, name=f'No duplicate donor_id {donor_id}',
            priority=ConstraintPriority.MANDATORY
        )
    _add_constraints_for_country_debt(path_id_to_path_with_score, path_id_to_var, config, ilp_model)
    possible = _add_constraints_for_required_patients(path_id_to_var, ilp_model, required_paths_per_recipient)
    if not possible:
        return
    matchings_to_search_for = min(config.max_number_of_matchings, config.max_matchings_in_all_solutions_solver)
    i = 0
    while i < matchings_to_search_for:
        solve_with_logging(ilp_model)

        status = mip_get_result_status(ilp_model)

        if status == Status.OPTIMAL:
            # check there is no violation, this is a hack, there should be no violation in optimal solution,
            # but it seems sometimes there is (but extremely rarely).
            #  https://github.com/mild-blue/txmatching/issues/1027

            constr_broken = False
            for constr in ilp_model.constrs:
                if constr.expr.violation > 0:
                    constr_broken = True
                    break
            i = i + 1
            selected_path_ids = [path_id for path_id, var in path_id_to_var.items() if mip_var_to_bool(var)]
            if not constr_broken:
                yield selected_path_ids
            missing = _add_constraints_removing_solution_return_missing_set(ilp_model, selected_path_ids,
                                                                            path_id_to_var)
            if missing == set():
                return
        else:
            break


def _add_constraints_removing_solution_return_missing_set(ilp_model: mip.Model,
                                                          selected_path_ids: List[int],
                                                          path_id_to_var: Dict[int, Var]) -> Set[int]:
    not_used_path_ids = set(path_id_to_var.keys()) - set(selected_path_ids)

    ilp_model.add_constr(mip.xsum([path_id_to_var[path_id] for path_id in not_used_path_ids]) >= 0.5)
    return not_used_path_ids


def _add_constraints_for_country_debt(path_id_to_path_with_score: Dict[int, PathWithScore],
                                      path_id_to_var: Dict[int, Var],
                                      config: ConfigParameters,
                                      ilp_model: mip.Model):
    countries_debt = {country for path_with_score in path_id_to_path_with_score.values()
                      for country in path_with_score.debt_per_country.keys()}

    countries_debt_zero = {country for path_with_score in path_id_to_path_with_score.values()
                           for country in path_with_score.debt_blood_zero_per_country.keys()}
    for country in countries_debt:
        debt_paths = _get_debt_paths(path_id_to_var, country, path_id_to_path_with_score, False)
        if debt_paths:
            ilp_model.add_constr(mip.xsum(debt_paths) <= config.max_debt_for_country, name=f'Max country debt'
                                                                                           f'for country {country}')
            ilp_model.add_constr(mip.xsum(debt_paths) >= - config.max_debt_for_country, name=f'Min country debt'
                                                                                             f'for country {country}')

    for country in countries_debt_zero:
        debt_paths = _get_debt_paths(path_id_to_var, country, path_id_to_path_with_score, True)
        if debt_paths:
            ilp_model.add_constr(mip.xsum(debt_paths) <= config.max_debt_for_country_for_blood_group_zero,
                                 name=f'Max blood group 0 country debt for country {country}')
            ilp_model.add_constr(mip.xsum(debt_paths) >= - config.max_debt_for_country_for_blood_group_zero,
                                 name=f'Min blood group 0 country debt for country {country}')


def _add_constraints_for_required_patients(path_id_to_var: Dict[int, Var],
                                           ilp_model: mip.Model,
                                           required_paths_per_recipient: List[List[int]]) -> bool:
    for required_donor_idxs_per_one_recipient in required_paths_per_recipient:
        if len(required_donor_idxs_per_one_recipient) > 0:
            ilp_model.add_constr(
                mip.xsum([path_id_to_var[path_id] for path_id in required_donor_idxs_per_one_recipient]) >= 1)
        else:
            return False
    return True


def _get_debt_paths(path_id_to_var: Dict[int, Var], country, path_id_to_path_with_score: Dict[int, PathWithScore],
                    take_blood_group_zero: bool = False):
    debt_paths = []
    if take_blood_group_zero:
        access_attribute_name = 'debt_blood_zero_per_country'
    else:
        access_attribute_name = 'debt_per_country'
    for path_id, var in path_id_to_var.items():
        country_debt = getattr(path_id_to_path_with_score[path_id], access_attribute_name).get(country, 0)
        if country_debt != 0:
            debt_paths.append(var * country_debt)
    return debt_paths
