import logging
from typing import Optional

from flask_restx import Resource

from txmatching.auth.auth_check import (require_valid_config_id,
                                        require_valid_txm_event_id)
from txmatching.auth.operation_guards.txm_event_guard import \
    guard_open_txm_event
from txmatching.auth.user.user_auth_check import \
    require_user_edit_config_access
from txmatching.data_transfer_objects.configuration.configuration_swagger import (
    ConfigIdPathParamDefinition, ConfigurationJson)
from txmatching.data_transfer_objects.shared_dto import (IdentifierDTOIn,
                                                         SuccessDTOOut)
from txmatching.data_transfer_objects.shared_swagger import (IdentifierJsonIn,
                                                             SuccessJsonOut)
from txmatching.database.services.config_service import (
    get_configuration_parameters_from_db_id_or_default, set_config_as_default)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.web.web_utils.namespaces import configuration_api
from txmatching.web.web_utils.route_utils import request_body, response_ok

logger = logging.getLogger(__name__)


@configuration_api.route('/<config_id>', methods=['GET'])
class ConfigurationApi(Resource):
    @configuration_api.doc(
        params={'config_id': ConfigIdPathParamDefinition},
    )
    @configuration_api.require_user_login()
    @configuration_api.response_ok(model=ConfigurationJson,
                                   description='Returns the specified matching configuration for the current user.')
    @configuration_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @require_valid_txm_event_id()
    @require_valid_config_id()
    def get(self, txm_event_id: int, config_id: Optional[int]) -> str:
        txm_event = get_txm_event_complete(txm_event_id)
        configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event=txm_event,
                                                                                      configuration_db_id=config_id)
        return response_ok(configuration_parameters)


@configuration_api.route('/set-default', methods=['PUT'])
class DefaultConfigurationApi(Resource):
    @configuration_api.doc(description='Set default configuration id for the txm event.')
    @configuration_api.require_user_login()
    @configuration_api.request_body(IdentifierJsonIn)
    @configuration_api.response_ok(SuccessJsonOut, description='Whether the update was successful')
    @configuration_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @require_user_edit_config_access()
    @require_valid_txm_event_id()
    def put(self, txm_event_id: int):
        identifier_dto = request_body(IdentifierDTOIn)
        guard_open_txm_event(txm_event_id)
        set_config_as_default(txm_event_id=txm_event_id, configuration_db_id=identifier_dto.id)
        return response_ok(SuccessDTOOut(success=True))
