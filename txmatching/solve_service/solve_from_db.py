import dataclasses
from typing import Iterable

from txmatching.database.db import db
from txmatching.database.services.config_service import (
    get_current_configuration, save_configuration_to_db)
from txmatching.database.services.patient_service import get_tx_session
from txmatching.database.services.scorer_service import score_matrix_to_dto
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.solve_service.data_objects.calculated_matchings import (
    CalculatedMatching, CalculatedMatchings)
from txmatching.solve_service.data_objects.donor_recipient import \
    DonorRecipient
from txmatching.solve_service.data_objects.solver_input_parameters import \
    SolverInputParameters
from txmatching.solve_service.solve_from_config import solve_from_config
from txmatching.solvers.matching.matching import Matching
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


def solve_from_db() -> Iterable[Matching]:
    tx_session = get_tx_session()

    current_configuration = get_current_configuration()
    current_config_matchings, score_matrix = solve_from_config(SolverInputParameters(
        donors_dict=tx_session.donors_dict,
        recipients_dict=tx_session.recipients_dict,
        configuration=current_configuration
    ))
    current_config_matchings_model = dataclasses.asdict(
        _current_config_matchings_to_model(current_config_matchings)
    )

    config_id = save_configuration_to_db(current_configuration, tx_session.db_id)
    pairing_result_model = PairingResultModel(
        score_matrix=score_matrix_to_dto(score_matrix),
        calculated_matchings=current_config_matchings_model,
        config_id=config_id,
        valid=True
    )
    db.session.add(pairing_result_model)
    db.session.commit()

    return current_config_matchings


def _current_config_matchings_to_model(config_matchings: Iterable[MatchingWithScore]) -> CalculatedMatchings:
    return CalculatedMatchings([
        CalculatedMatching(
            donors_recipients=[
                DonorRecipient(donor.db_id, recipient.db_id)
                for donor, recipient in final_solution.donor_recipient_list
            ],
            score=final_solution.score(),
            db_id=final_solution.db_id()
        )
        for final_solution in config_matchings
    ])
