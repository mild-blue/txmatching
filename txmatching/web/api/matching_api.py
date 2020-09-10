# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import dataclasses
import logging

from flask import request, jsonify
from flask_restx import Resource


from txmatching.data_transfer_objects.configuration.configuration_swagger import CONFIGURATION_JSON
from txmatching.data_transfer_objects.matchings.matching_dto import (
    MatchingDTO, RoundDTO, Transplant)
from txmatching.data_transfer_objects.matchings.matching_swagger import MATCHING_MODEL
from txmatching.database.services.config_service import \
    save_configuration_as_current, configuration_from_dict
from txmatching.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.web.api.namespaces import matching_api
from txmatching.web.auth.login_check import login_required

logger = logging.getLogger(__name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@matching_api.route('/calculate-for-config', methods=['POST'])
class CalculateFromConfig(Resource):
    @matching_api.doc(body=CONFIGURATION_JSON, security='bearer')
    @matching_api.response(200, model=MATCHING_MODEL, description='')
    @login_required()
    def post(self) -> str:
        configuration = configuration_from_dict(request.json)
        save_configuration_as_current(configuration)
        solve_from_db()
        matchings, score_dict, compatible_blood_dict = get_latest_matchings_and_score_matrix()

        matching_dtos = [
            dataclasses.asdict(MatchingDTO(
                rounds=[
                    RoundDTO(
                        transplants=[
                            Transplant(
                                score_dict[(donor.db_id, recipient.db_id)],
                                compatible_blood_dict[(donor.db_id, recipient.db_id)],
                                donor.medical_id,
                                recipient.medical_id) for donor, recipient in matching_round.donor_recipient_list])
                    for matching_round in matching.get_rounds()],
                countries=matching.get_country_codes_counts(),
                score=matching.score()
            )) for matching in matchings
        ]

        return jsonify(matching_dtos)
