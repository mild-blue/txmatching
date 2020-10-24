import dataclasses
from typing import Iterable

from txmatching.data_transfer_objects.matchings.calculated_matchings_dto import (
    CalculatedMatchingDTO, CalculatedMatchingsDTO)
from txmatching.data_transfer_objects.matchings.donor_recipient_dto import \
    DonorRecipientDTO
from txmatching.database.db import db
from txmatching.database.services.config_service import \
    save_configuration_to_db
from txmatching.database.services.scorer_service import score_matrix_to_dto
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.pairing_result import PairingResult


def save_pairing_result(pairing_result: PairingResult):
    calculated_matchings_model = dataclasses.asdict(
        _calculated_matchings_to_model(pairing_result.calculated_matchings)
    )

    config_id = save_configuration_to_db(pairing_result.configuration, pairing_result.txm_event_db_id)

    pairing_result_model = PairingResultModel(
        score_matrix=score_matrix_to_dto(pairing_result.score_matrix),
        calculated_matchings=calculated_matchings_model,
        config_id=config_id,
        valid=True
    )
    db.session.add(pairing_result_model)
    db.session.commit()


def _calculated_matchings_to_model(calculated_matchings: Iterable[MatchingWithScore]) -> CalculatedMatchingsDTO:
    return CalculatedMatchingsDTO([
        CalculatedMatchingDTO(
            donors_recipients=[
                DonorRecipientDTO(pair.donor.db_id, pair.recipient.db_id)
                for pair in matching.get_donor_recipient_pairs()
            ],
            score=matching.score(),
            db_id=matching.order_id()
        )
        for matching in calculated_matchings
    ])
