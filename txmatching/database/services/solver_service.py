import dataclasses

from txmatching.data_transfer_objects.matchings.donor_recipient_model import \
    DonorRecipientModel
from txmatching.data_transfer_objects.matchings.matchings_model import (
    MatchingModel, MatchingsModel)
from txmatching.database.db import db
from txmatching.database.services.config_service import \
    save_configuration_to_db
from txmatching.database.services.scorer_service import score_matrix_to_dto
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.solvers.pairing_result import PairingResult


def save_pairing_result(pairing_result: PairingResult, user_id: int):
    calculated_matchings_model = dataclasses.asdict(
        _calculated_matchings_to_model(pairing_result)
    )

    txm_event = get_txm_event_complete(pairing_result.txm_event_db_id)
    config_id = save_configuration_to_db(pairing_result.configuration, txm_event, user_id)

    pairing_result_model = PairingResultModel(
        score_matrix=score_matrix_to_dto(pairing_result.score_matrix),
        calculated_matchings=calculated_matchings_model,
        config_id=config_id,
        valid=True
    )
    db.session.add(pairing_result_model)
    db.session.commit()


def _calculated_matchings_to_model(pairing_result: PairingResult) -> MatchingsModel:
    return MatchingsModel([
        MatchingModel(
            donors_recipients=[
                DonorRecipientModel(pair.donor.db_id, pair.recipient.db_id)
                for pair in matching.get_donor_recipient_pairs()
            ],
            score=matching.score(),
            db_id=matching.order_id()
        )
        for matching in pairing_result.calculated_matchings_list
    ],
        found_matchings_count=pairing_result.found_matchings_count,
        show_not_all_matchings_found=not pairing_result.all_results_found
    )
