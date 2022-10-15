import logging
from typing import Optional

from flask_restx import Resource

from txmatching.auth.auth_check import require_valid_txm_event_id
from txmatching.auth.data_types import UserRole
from txmatching.auth.request_context import get_user_role
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.data_transfer_objects.configuration.configuration_swagger import (
    ConfigIdPathParamDefinition, ConfigurationJson)
from txmatching.data_transfer_objects.matchings.matching_swagger import \
    CalculatedMatchingsJson
from txmatching.database.services.config_service import \
    get_configuration_from_db_id_or_default
from txmatching.database.services.matching_service import (
    create_calculated_matchings_dto,
    get_matchings_detailed_for_pairing_result_model)
from txmatching.database.services.pairing_result_service import \
    get_pairing_result_comparable_to_config_or_solve
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.web_utils.namespaces import matching_api
from txmatching.web.web_utils.route_utils import response_ok

logger = logging.getLogger(__name__)


@matching_api.route('/calculate-for-config/<config_id>', methods=['GET'])
class CalculateFromConfig(Resource):
    @matching_api.doc(
        params={'config_id': ConfigIdPathParamDefinition},
    )
    @matching_api.require_user_login()
    @matching_api.response_ok(CalculatedMatchingsJson, 'List of all matchings for given configuration.')
    @matching_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @require_valid_txm_event_id()
    def get(self, txm_event_id: int, config_id: Optional[int]) -> str:
        txm_event = get_txm_event_complete(txm_event_id)
        user_id = get_current_user_id()

        # 1. Get or save config
        configuration = get_configuration_from_db_id_or_default(txm_event, config_id)

        # 2. Get or solve pairing result
        pairing_result_model = get_pairing_result_comparable_to_config_or_solve(configuration, txm_event)

        # 3. Get matchings detailed from pairing_result_model
        matchings_detailed = get_matchings_detailed_for_pairing_result_model(pairing_result_model, txm_event)

        calculated_matchings_dto = create_calculated_matchings_dto(matchings_detailed, matchings_detailed.matchings,
                                                                   configuration.id)
        calculated_matchings_dto.calculated_matchings = calculated_matchings_dto.calculated_matchings[
            :configuration.parameters.max_number_of_matchings]
        if get_user_role() == UserRole.VIEWER:
            calculated_matchings_dto.calculated_matchings = calculated_matchings_dto.calculated_matchings[
                :configuration.parameters.max_matchings_to_show_to_viewer]
            calculated_matchings_dto.show_not_all_matchings_found = False
        logging.debug('Collected matchings and sending them')
        return response_ok(calculated_matchings_dto)
