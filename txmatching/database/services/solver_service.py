import dataclasses
from typing import Iterable

from txmatching.database.db import db
from txmatching.database.services.config_service import \
    save_configuration_to_db
from txmatching.database.services.scorer_service import score_matrix_to_dto
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.solve_service.data_objects.calculated_matchings import (
    CalculatedMatching, CalculatedMatchings)
from txmatching.solve_service.data_objects.donor_recipient import \
    DonorRecipient
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.pairing_result import PairingResult


def save_pairing_result(pairing_result: PairingResult):
    current_config_matchings_model = dataclasses.asdict(
        _current_config_matchings_to_model(pairing_result.calculated_matchings)
    )

    config_id = save_configuration_to_db(pairing_result.configuration, pairing_result.txm_event_db_id)
    pairing_result_model = PairingResultModel(
        score_matrix=score_matrix_to_dto(pairing_result.score_matrix),
        calculated_matchings=current_config_matchings_model,
        config_id=config_id,
        valid=True
    )
    db.session.add(pairing_result_model)
    db.session.commit()


def _current_config_matchings_to_model(config_matchings: Iterable[MatchingWithScore]) -> CalculatedMatchings:
    return CalculatedMatchings([
        CalculatedMatching(
            donors_recipients=[
                DonorRecipient(donor.db_id, recipient.db_id)
                for donor, recipient in final_solution.donor_recipient_list
            ],
            score=final_solution.score(),
            db_id=final_solution.order_id()
        )
        for final_solution in config_matchings
    ])
