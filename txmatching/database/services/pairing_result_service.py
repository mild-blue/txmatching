import dataclasses
import logging
from typing import Optional

from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.matchings.donor_recipient_model import \
    DonorRecipientModel
from txmatching.data_transfer_objects.matchings.matchings_model import (
    MatchingModel, MatchingsModel)
from txmatching.database.db import db
from txmatching.database.services.config_service import (
    configuration_from_config_model, get_configuration_from_db_id)
from txmatching.database.services.patient_service import \
    get_patients_persistent_hash
from txmatching.database.services.scorer_service import score_matrix_to_dict
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.patients.patient import TxmEvent
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.solvers.pairing_result import PairingResult

logger = logging.getLogger(__name__)


def get_pairing_result_comparable_to_config_or_solve(
        config_id: int,
        txm_event: TxmEvent
) -> PairingResultModel:
    configuration = get_configuration_from_db_id(config_id, txm_event.db_id)

    maybe_pairing_result_model = get_pairing_result_comparable_to_config(config_id, configuration, txm_event)
    if maybe_pairing_result_model is not None:
        return maybe_pairing_result_model
    else:
        return solve_from_config_id_and_save(config_id, configuration, txm_event)


def get_pairing_result_comparable_to_config(
        config_id: int,
        configuration: Configuration,
        txm_event: TxmEvent
) -> Optional[PairingResultModel]:
    logger.debug(f'Searching pairing result models comparable to configuration {config_id}')
    patients_hash = get_patients_persistent_hash(txm_event)
    pairing_result_models = PairingResultModel.query.filter(
        PairingResultModel.patients_hash == patients_hash
    ).all()

    for pairing_result_model in pairing_result_models:  # type: PairingResultModel
        config_from_model = configuration_from_config_model(pairing_result_model.original_config)
        if configuration.comparable(config_from_model):
            logger.debug(f'Found pairing result with id {pairing_result_model.id} '
                         f'comparable to configuration {config_id}')
            return pairing_result_model

    logger.info(f'Pairing result for patients hash {patients_hash} and '
                f'configuration comparable to config id {config_id} is not in db yet')
    return None


def solve_from_config_id_and_save(
        config_id: int,
        configuration: Configuration,
        txm_event: TxmEvent
) -> PairingResultModel:
    pairing_result = solve_from_configuration(configuration, txm_event=txm_event)
    pairing_result_model = _save_pairing_result(pairing_result, config_id, txm_event)
    logger.info(f'Pairing was solved from configuration {config_id} '
                f'and saved as pairing result {pairing_result_model.id}')
    return pairing_result_model


def _save_pairing_result(
        pairing_result: PairingResult,
        original_config_id: int,
        txm_event: TxmEvent
) -> PairingResultModel:
    calculated_matchings_model = dataclasses.asdict(
        _calculated_matchings_to_model(pairing_result)
    )
    patients_hash = get_patients_persistent_hash(txm_event)

    pairing_result_model = PairingResultModel(
        score_matrix=score_matrix_to_dict(pairing_result.score_matrix),
        calculated_matchings=calculated_matchings_model,
        original_config_id=original_config_id,
        patients_hash=patients_hash,
        valid=True
    )
    db.session.add(pairing_result_model)
    db.session.commit()

    return pairing_result_model


def _calculated_matchings_to_model(pairing_result: PairingResult) -> MatchingsModel:
    return MatchingsModel([
        MatchingModel(
            donors_recipients=[
                DonorRecipientModel(pair.donor.db_id, pair.recipient.db_id)
                for pair in matching.get_donor_recipient_pairs()
            ],
            score=matching.score,
            db_id=matching.order_id
        )
        for matching in pairing_result.calculated_matchings_list
    ],
        found_matchings_count=pairing_result.found_matchings_count,
        show_not_all_matchings_found=not pairing_result.all_results_found
    )
