import logging

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import TxmEvent
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solve_service.solver_lock import run_with_solver_lock
from txmatching.solvers.pairing_result import PairingResult
from txmatching.solvers.solver_from_config import solver_from_configuration

logger = logging.getLogger(__name__)


def solve_from_configuration(config_parameters: ConfigParameters, txm_event: TxmEvent) -> PairingResult:
    return run_with_solver_lock(lambda: _solve_from_configuration_unsafe(config_parameters, txm_event))


def _solve_from_configuration_unsafe(config_parameters: ConfigParameters, txm_event: TxmEvent) -> PairingResult:
    # remove invalid patients from config (if there are any)
    config_parameters.required_patient_db_ids = [patient_db_id for patient_db_id in config_parameters.required_patient_db_ids
                                                 if patient_db_id in txm_event.active_and_valid_recipients_dict]
    config_parameters.manual_donor_recipient_scores = [pair for pair in config_parameters.manual_donor_recipient_scores
                                                       if pair.donor_db_id in txm_event.active_and_valid_donors_dict
                                                       and pair.recipient_db_id in txm_event.active_and_valid_recipients_dict]

    scorer = scorer_from_configuration(config_parameters)
    solver = solver_from_configuration(config_parameters,
                                       donors_dict=txm_event.active_and_valid_donors_dict,
                                       recipients_dict=txm_event.active_and_valid_recipients_dict,
                                       scorer=scorer)

    all_matchings = list(solver.solve())

    for idx, matching_in_good_order in enumerate(all_matchings):
        matching_in_good_order.set_order_id(idx + 1)

    logger.info(f'{len(all_matchings)} matchings were found.')

    return PairingResult(configuration=config_parameters,
                         compatibility_graph=solver.compatibility_graph,
                         calculated_matchings_list=all_matchings,
                         txm_event_db_id=txm_event.db_id)
