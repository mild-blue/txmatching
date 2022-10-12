import logging
import tempfile
from os import close, dup, dup2
from typing import Dict, List, Set

import mip
from mip import Var

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.solvers.all_solutions_solver.compatibility_graph_utils import \
    PathWithScore
from txmatching.solvers.ilp_solver.mip_utils import (mip_get_result_status,
                                                     mip_var_to_bool)
from txmatching.solvers.ilp_solver.solution import Status

logger = logging.getLogger(__name__)


def optimise_paths(paths_with_the_same_donors: List[List[int]], path_id_to_path_with_score: Dict[int, PathWithScore],
                   config: ConfigParameters):
    """Build and solve the lexicographic optimisation integer programming model.

    Parameters:
    ntpo -- number of possible cycles/chains
    incomp -- list containing the incompatibilities between cycles/chains
    weights -- weights of the cycles/chains according to the the criteria given in lexicographic order
    """

    # model
    ilp_model = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)
    path_id_to_var = {}
    for path_id in path_id_to_path_with_score:
        path_id_to_var[path_id] = ilp_model.add_var(var_type=mip.BINARY, name=str(path_id))

    max_score = max(path_info.score for path_info in path_id_to_path_with_score.values())
    donor_count = sum(path_info.length for path_info in path_id_to_path_with_score.values())

    number_of_transplants_multiplier = max_score * donor_count
    ilp_model.objective = mip.xsum(
        var * (path_id_to_path_with_score[path_id].score +
               number_of_transplants_multiplier * path_id_to_path_with_score[path_id].length)
        for path_id, var in path_id_to_var.items()
    )
    for var in path_id_to_var.values():
        ilp_model.add_constr(var <= 1)

    for paths_with_the_same_donor in paths_with_the_same_donors:
        ilp_model.add_constr(
            mip.xsum([path_id_to_var[path] for path in paths_with_the_same_donor]) <= 1
        )
    _add_constraints_for_country_debt(path_id_to_path_with_score, path_id_to_var, config, ilp_model)
    matchings_to_search_for = config.max_matchings_in_all_solutions_solver
    for _ in range(matchings_to_search_for):
        _solve_with_logging(ilp_model)

        status = mip_get_result_status(ilp_model)

        if status == Status.OPTIMAL:
            selected_path_ids = [path_id for path_id, var in path_id_to_var.items() if mip_var_to_bool(var)]
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
            ilp_model.add_constr(mip.xsum(debt_paths) <= config.max_debt_for_country)

    for country in countries_debt_zero:
        debt_paths = _get_debt_paths(path_id_to_var, country, path_id_to_path_with_score, True)
        if debt_paths:
            ilp_model.add_constr(mip.xsum(debt_paths) <= config.max_debt_for_country_for_blood_group_zero)


def _get_debt_paths(path_id_to_var: Dict[int, Var], country, path_id_to_path_with_score: Dict[int, PathWithScore],
                    take_blood_group_zero: bool = False):
    debt_paths = []
    if take_blood_group_zero:
        access_attribute_name = 'debt_blood_zero_per_country'
    else:
        access_attribute_name = 'debt_per_country'
    for path_id, var in path_id_to_var.items():
        country_debt_dict = getattr(path_id_to_path_with_score[path_id], access_attribute_name)
        if country in country_debt_dict:
            debt_paths.append(var * country_debt_dict[country])
    return debt_paths
