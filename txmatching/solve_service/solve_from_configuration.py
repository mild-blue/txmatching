import heapq
import logging
from typing import Iterator, List, Optional, Tuple

from txmatching.configuration.configuration import Configuration
from txmatching.filters.filter_base import FilterBase
from txmatching.filters.filter_from_config import filter_from_config
from txmatching.patients.patient import TxmEvent
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solve_service.solver_lock import run_with_solver_lock
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.pairing_result import PairingResult
from txmatching.solvers.solver_from_config import solver_from_configuration
from txmatching.utils.enums import Solver

logger = logging.getLogger(__name__)


def solve_from_configuration(configuration: Configuration, txm_event: TxmEvent) -> PairingResult:
    return run_with_solver_lock(lambda: _solve_from_configuration_unsafe(configuration, txm_event))


def _solve_from_configuration_unsafe(configuration: Configuration, txm_event: TxmEvent) -> PairingResult:
    scorer = scorer_from_configuration(configuration)
    solver = solver_from_configuration(configuration,
                                       donors_dict=txm_event.active_donors_dict,
                                       recipients_dict=txm_event.active_recipients_dict,
                                       scorer=scorer)

    all_matchings = solver.solve()
    matching_filter = filter_from_config(configuration)

    matchings_filtered_sorted, all_results_found, matching_count = _filter_and_sort_matchings(
        all_matchings,
        matching_filter,
        configuration)

    logger.info(f'{len(matchings_filtered_sorted)} matchings were found.')

    return PairingResult(configuration=configuration,
                         score_matrix=solver.score_matrix,
                         calculated_matchings_list=matchings_filtered_sorted,
                         txm_event_db_id=txm_event.db_id,
                         all_results_found=all_results_found,
                         found_matchings_count=matching_count)


def _filter_and_sort_matchings(all_matchings: Iterator[MatchingWithScore],
                               matching_filter: FilterBase,
                               configuration: Configuration
                               ) -> Tuple[List[MatchingWithScore], bool, Optional[int]]:
    matchings_heap = []
    all_results_found = True
    i = -1
    for i, matching in enumerate(all_matchings):
        if matching_filter.keep(matching):
            matching_entry = (
                len(matching.get_donor_recipient_pairs()),
                matching.score,
                len(matching.get_rounds()),
                i,  # we want to skip sorting by matching
                matching
            )

            heapq.heappush(matchings_heap, matching_entry)
            if len(matchings_heap) > configuration.max_number_of_matchings:
                heapq.heappop(matchings_heap)

            if i % 100000 == 0:
                logger.info(f'Processed {i} matchings')

            if i == configuration.max_matchings_in_all_solutions_solver - 1:
                logger.error(
                    f'Max number of matchings {configuration.max_matchings_in_all_solutions_solver} was reached. '
                    f'Returning only best {configuration.max_number_of_matchings} matchings from '
                    f'{configuration.max_matchings_in_all_solutions_solver} found up to now.')
                all_results_found = False
                break

    matchings = [matching for _, _, _, _, matching in sorted(matchings_heap, reverse=True)]
    for idx, matching_in_good_order in enumerate(matchings):
        matching_in_good_order.set_order_id(idx + 1)

    if configuration.solver_constructor_name == Solver.ILPSolver:
        result_count = None
    else:
        result_count = i + 1

    return matchings, all_results_found, result_count
