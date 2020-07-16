from typing import List

from kidney_exchange.database.services.config_service import get_current_configuration
from kidney_exchange.database.services.services_for_solve import db_matchings_to_matching_list
from kidney_exchange.database.sql_alchemy_schema import PairingResultModel
from kidney_exchange.scorers.scorer_from_config import scorer_from_configuration
from kidney_exchange.solvers.matching.matching import Matching
from kidney_exchange.solvers.solve_from_config import solve_from_db


def get_latest_matchings() -> List[Matching]:
    last_pairing_result_model = PairingResultModel.query.order_by(PairingResultModel.updated_at.desc()).first()
    if last_pairing_result_model is None:
        solve_from_db()
        last_pairing_result_model = PairingResultModel.query.order_by(PairingResultModel.updated_at.desc()).first()
    all_matchings = db_matchings_to_matching_list(last_pairing_result_model.calculated_matchings)
    configuration = get_current_configuration()
    scorer = scorer_from_configuration(configuration)

    all_matchings.sort(key=lambda matching: scorer.score(matching), reverse=True)
    all_matchings.sort(key=lambda matching: len(matching.get_rounds()), reverse=True)
    all_matchings.sort(key=lambda matching: len(matching.donor_recipient_list), reverse=True)
    return all_matchings[:20]
