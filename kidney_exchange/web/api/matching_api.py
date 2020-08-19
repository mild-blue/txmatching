import dataclasses
import json
import logging

from flask import request, Response, Blueprint
from flask_restx import Resource

from kidney_exchange.data_transfer_objects.configuration.configuration_swagger import CONFIGURATION_MODEL
from kidney_exchange.data_transfer_objects.configuration.configuration_from_dto import \
    configuration_from_dto
from kidney_exchange.data_transfer_objects.matchings.matching_swagger import MATCHING_MODEL
from kidney_exchange.data_transfer_objects.matchings.matching_dto import (
    MatchingDTO, RoundDTO, Transplant)
from kidney_exchange.database.services.config_service import \
    save_configuration_as_current
from kidney_exchange.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from kidney_exchange.solve_service.solve_from_db import solve_from_db
from kidney_exchange.web.api.namespaces import matching_api, MATCHING_NAMESPACE
logger = logging.getLogger(__name__)

matching_blueprint = Blueprint(MATCHING_NAMESPACE, __name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


@matching_api.route('/calculate-for-config', methods=['POST'])
class CalculateFromConfig(Resource):
    @matching_api.doc(body=CONFIGURATION_MODEL)
    @matching_api.response(200, model=MATCHING_MODEL, description="")
    def post(self) -> str:
        configuration = configuration_from_dto(request.json)
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
                                recipient.medical_id) for donor, recipient in round.donor_recipient_list])
                    for round in matching.get_rounds()],
                countries=matching.get_country_codes_counts(),
                score=matching.score()
            )) for matching in matchings
        ]

        json_data = json.dumps(matching_dtos)

        return Response(json_data, mimetype='application/json')
