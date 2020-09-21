# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import request, jsonify
from flask_restx import Resource

from txmatching.auth.data_types import UserRole
from txmatching.auth.login_check import login_required, get_user_role
from txmatching.data_transfer_objects.configuration.configuration_swagger import CONFIGURATION_JSON
from txmatching.data_transfer_objects.matchings.matching_swagger import MATCHING_MODEL
from txmatching.database.services.config_service import \
    save_configuration_as_current, configuration_from_dict
from txmatching.database.services.matching_service import \
    get_latest_matchings_and_score_matrix, get_matching_dtos
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.web.api.namespaces import matching_api

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

        matching_dtos = get_matching_dtos(matchings, score_dict, compatible_blood_dict)
        if get_user_role() == UserRole.VIEWER:
            matching_dtos = matching_dtos[:configuration.max_matchings_to_show_to_viewer]

        return jsonify(matching_dtos)
