import logging
from typing import Iterator, List, Tuple

from txmatching.configuration.configuration import Configuration
from txmatching.database.services.txm_event_service import get_txm_event
from txmatching.filters.filter_base import FilterBase
from txmatching.filters.filter_from_config import filter_from_config
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.pairing_result import PairingResult
from txmatching.solvers.solver_from_config import solver_from_configuration

logger = logging.getLogger(__name__)
MAX_ALLOWED_NUMBER_OF_MATCHINGS = 800
MAX_NUMBER_OF_MATCHINGS_TO_STORE = 400


def solve_from_configuration(configuration: Configuration, txm_event_db_id: int) -> PairingResult:
    txm_event = get_txm_event(txm_event_db_id)
    scorer = scorer_from_configuration(configuration)
    solver = solver_from_configuration(configuration,
                                       donors_dict=txm_event.active_donors_dict,
                                       recipients_dict=txm_event.active_recipients_dict,
                                       scorer=scorer)

    all_matchings = solver.solve()
    matching_filter = filter_from_config(configuration)

    matchings_filtered, all_results_found, matching_count = _filter_and_limit_number_of_matchings(all_matchings,
                                                                                                  matching_filter)

    matchings_filtered_sorted = _sort_matchings_by_transplant_number_and_score(matchings_filtered)

    logger.info(f'{matching_count} matchings were found.')

    return PairingResult(configuration=configuration,
                         score_matrix=solver.score_matrix,
                         calculated_matchings_list=matchings_filtered_sorted,
                         txm_event_db_id=txm_event.db_id,
                         all_results_found=all_results_found,
                         found_matchings_count=matching_count)


def _filter_and_limit_number_of_matchings(all_matchings: Iterator[MatchingWithScore],
                                          matching_filter: FilterBase
                                          ) -> Tuple[List[MatchingWithScore], bool, int]:
    matchings = []
    all_results_found = True
    i = -1
    # TODO here we should use something more memory efficient, never really store the whole list
    # https://github.com/mild-blue/txmatching/issues/356
    for i, matching in enumerate(all_matchings):
        if matching_filter.keep(matching):
            matchings.append(matching)
            if i == MAX_ALLOWED_NUMBER_OF_MATCHINGS - 1:
                logger.error(f'Max number of matchings {MAX_ALLOWED_NUMBER_OF_MATCHINGS} was reached. Returning only '
                             f'matchings found up to now.')
                all_results_found = False
                break

    return matchings, all_results_found, i + 1


def _sort_matchings_by_transplant_number_and_score(matchings: Iterator[MatchingWithScore]) -> List[MatchingWithScore]:
    # TODO here we should use something more memory efficient, never really store the whole list
    # https://github.com/mild-blue/txmatching/issues/356
    matchings = sorted(matchings, key=lambda matching: len(matching.get_rounds()), reverse=True)
    matchings = sorted(matchings, key=lambda matching: matching.score(), reverse=True)
    matchings = sorted(matchings, key=lambda matching: len(matching.get_donor_recipient_pairs()), reverse=True)
    for idx, matching_in_good_order in enumerate(matchings):
        matching_in_good_order.set_order_id(idx + 1)
    return matchings[:MAX_NUMBER_OF_MATCHINGS_TO_STORE]
