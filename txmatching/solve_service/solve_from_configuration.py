import logging
from typing import Iterable, List

from txmatching.configuration.configuration import Configuration
from txmatching.database.services.matching_service import \
    load_matching_for_config_from_db
from txmatching.database.services.patient_service import get_txm_event
from txmatching.filters.filter_from_config import filter_from_config
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.pairing_result import PairingResult
from txmatching.solvers.solver_from_config import solver_from_configuration

logger = logging.getLogger(__name__)


def solve_from_configuration(configuration: Configuration, txm_event_db_id: int) -> PairingResult:
    txm_event = get_txm_event(txm_event_db_id)
    scorer = scorer_from_configuration(configuration)
    solver = solver_from_configuration(configuration,
                                       donors_dict=txm_event.donors_dict,
                                       recipients_dict=txm_event.recipients_dict,
                                       scorer=scorer)
    matchings_in_db = load_matching_for_config_from_db(txm_event, configuration)
    if matchings_in_db is not None:
        all_solutions = matchings_in_db
    else:
        all_solutions = solver.solve()

    matching_filter = filter_from_config(configuration)
    matchings_filtered = filter(matching_filter.keep, all_solutions)
    matchings_filtered_sorted = _sort_matchings_by_transplant_number_and_score(matchings_filtered)

    return PairingResult(configuration=configuration,
                         score_matrix=solver.score_matrix,
                         calculated_matchings=matchings_filtered_sorted,
                         txm_event_db_id=txm_event.db_id)


def _sort_matchings_by_transplant_number_and_score(matchings: Iterable[MatchingWithScore]) -> List[MatchingWithScore]:
    matchings = sorted(matchings, key=lambda matching: len(matching.get_rounds()), reverse=True)
    matchings = sorted(matchings, key=lambda matching: matching.score(), reverse=True)
    matchings = sorted(matchings, key=lambda matching: len(matching.get_donor_recipient_pairs()), reverse=True)
    for idx, matching_in_good_order in enumerate(matchings):
        matching_in_good_order.set_order_id(idx + 1)
    return matchings
