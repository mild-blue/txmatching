# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.

import logging

from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.data_types import UserRole
from txmatching.auth.request_context import get_user_role
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigurationJson
from txmatching.data_transfer_objects.matchings.matching_swagger import \
    CalculatedMatchingsJson
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    FailJson
from txmatching.database.services import solver_service
from txmatching.database.services.config_service import (
    configuration_from_dict, find_configuration_db_id_for_configuration)
from txmatching.database.services.matching_service import (
    create_calculated_matchings_dto, get_latest_matchings_detailed,
    get_matchings_detailed_for_configuration)
from txmatching.database.services.txm_event_service import (
    get_txm_event, get_txm_event_id_for_current_user)
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.api.namespaces import matching_api

logger = logging.getLogger(__name__)


@matching_api.route('/calculate-for-config', methods=['POST'])
class CalculateFromConfig(Resource):
    @matching_api.doc(body=ConfigurationJson, security='bearer')
    @matching_api.response(200, model=CalculatedMatchingsJson,
                           description='List of all matchings for given configuration.')
    @matching_api.response(code=400, model=FailJson, description='Wrong data format.')
    @matching_api.response(code=401, model=FailJson, description='Authentication failed.')
    @matching_api.response(
        code=403,
        model=FailJson,
        description='Access denied. You do not have rights to access this endpoint.'
    )
    @matching_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def post(self) -> str:
        txm_event_db_id = get_txm_event_id_for_current_user()
        txm_event = get_txm_event(txm_event_db_id)
        user_id = get_current_user_id()
        configuration = configuration_from_dict(request.json)
        maybe_configuration_db_id = find_configuration_db_id_for_configuration(txm_event=txm_event,
                                                                               configuration=configuration)
        if maybe_configuration_db_id:
            matchings_detailed = get_matchings_detailed_for_configuration(txm_event, maybe_configuration_db_id)
        else:
            pairing_result = solve_from_configuration(configuration, txm_event=txm_event)
            solver_service.save_pairing_result(pairing_result, user_id)
            # TODO here there is not reason to load the data again from the database. Fix that
            matchings_detailed = get_latest_matchings_detailed(txm_event)

        calculated_matchings_dto = create_calculated_matchings_dto(matchings_detailed, matchings_detailed.matchings)

        if get_user_role() == UserRole.VIEWER:
            calculated_matchings_dto.calculated_matchings = calculated_matchings_dto.calculated_matchings[
                                                            :configuration.max_matchings_to_show_to_viewer]

        return jsonify(calculated_matchings_dto)
