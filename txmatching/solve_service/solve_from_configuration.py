import heapq
import logging
from typing import Iterator, List, Optional, Tuple

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.filters.filter_base import FilterBase
from txmatching.filters.filter_from_config import filter_from_config
from txmatching.patients.patient import TxmEvent
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solve_service.solver_lock import run_with_solver_lock
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.pairing_result import PairingResult
from txmatching.solvers.solver_from_config import solver_from_configuration

logger = logging.getLogger(__name__)


def solve_from_configuration(config_parameters: ConfigParameters, txm_event: TxmEvent) -> PairingResult:
    return run_with_solver_lock(lambda: _solve_from_configuration_unsafe(config_parameters, txm_event))


def _solve_from_configuration_unsafe(config_parameters: ConfigParameters, txm_event: TxmEvent) -> PairingResult:
    # check if there are invalid patients in the config
    for patient_db_id in config_parameters.required_patient_db_ids:
        if patient_db_id not in txm_event.active_and_valid_recipients_dict:
            config_parameters.required_patient_db_ids.remove(patient_db_id)

    for pair in config_parameters.manual_donor_recipient_scores:
        if pair.donor_db_id not in txm_event.active_and_valid_donors_dict \
            and pair.recipient_db_id not in txm_event.active_and_valid_recipients_dict:
            config_parameters.manual_donor_recipient_scores.remove(pair)

    scorer = scorer_from_configuration(config_parameters)
    solver = solver_from_configuration(config_parameters,
                                       donors_dict=txm_event.active_and_valid_donors_dict,
                                       recipients_dict=txm_event.active_and_valid_recipients_dict,
                                       scorer=scorer)

    all_matchings = solver.solve()
    matching_filter = filter_from_config(config_parameters)

    matchings_filtered_sorted, all_results_found, matching_count = _filter_and_sort_matchings(
        all_matchings,
        matching_filter,
        config_parameters)

    logger.info(f'{len(matchings_filtered_sorted)} matchings were found.')

    return PairingResult(configuration=config_parameters,
                         compatibility_graph=solver.compatibility_graph,
                         calculated_matchings_list=matchings_filtered_sorted,
                         txm_event_db_id=txm_event.db_id,
                         all_results_found=all_results_found,
                         found_matchings_count=matching_count)


def _filter_and_sort_matchings(all_matchings: Iterator[MatchingWithScore],
                               matching_filter: FilterBase,
                               config_parameters: ConfigParameters
                               ) -> Tuple[List[MatchingWithScore], bool, Optional[int]]:
    matchings_heap = []
    # Obsolete parameters, remove in https://github.com/mild-blue/txmatching/issues/1028, result count made sense
    # only when all solutions solver was really looking for all solutions.
    result_count = None
    all_results_found = True
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
            if len(matchings_heap) > config_parameters.max_number_of_matchings:
                heapq.heappop(matchings_heap)

            if i % 100000 == 0:
                logger.info(f'Processed {i} matchings')

    matchings = [matching for _, _, _, _, matching in sorted(matchings_heap, reverse=True)]
    for idx, matching_in_good_order in enumerate(matchings):
        matching_in_good_order.set_order_id(idx + 1)

    return matchings, all_results_found, result_count
