# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import dataclasses
import logging

from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.data_types import UserRole
from txmatching.auth.request_context import get_user_role
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigurationJson
from txmatching.data_transfer_objects.matchings.matching_dto import (
    MatchingDTO, RoundDTO, TransplantDTOOut)
from txmatching.data_transfer_objects.matchings.matching_swagger import \
    Matchings
from txmatching.database.services.config_service import configuration_from_dict
from txmatching.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from txmatching.database.services.txm_event_service import \
    get_txm_event_for_current_user
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.web.api.namespaces import matching_api

logger = logging.getLogger(__name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@matching_api.route('/calculate-for-config', methods=['POST'])
class CalculateFromConfig(Resource):
    @matching_api.doc(body=ConfigurationJson, security='bearer')
    @matching_api.response(200, model=Matchings, description='List of all matching for given configuration')
    @require_user_login()
    def post(self) -> str:
        txm_event_id = get_txm_event_for_current_user()
        configuration = configuration_from_dict(request.json)
        solve_from_db(configuration, txm_event_db_id=txm_event_id)
        matchings, score_dict, compatible_blood_dict = get_latest_matchings_and_score_matrix(txm_event_id)

        matching_dtos = [
            dataclasses.asdict(MatchingDTO(
                rounds=[
                    RoundDTO(
                        transplants=[
                            TransplantDTOOut(
                                score_dict[(donor.db_id, recipient.db_id)],
                                compatible_blood_dict[(donor.db_id, recipient.db_id)],
                                donor.medical_id,
                                recipient.medical_id) for donor, recipient in matching_round.donor_recipient_list])
                    for matching_round in matching.get_rounds()],
                countries=matching.get_country_codes_counts(),
                score=matching.score(),
                order_id=matching.order_id()
            )) for matching in matchings
        ]
        if get_user_role() == UserRole.VIEWER:
            matching_dtos = matching_dtos[:configuration.max_matchings_to_show_to_viewer]

        return jsonify(matching_dtos)
