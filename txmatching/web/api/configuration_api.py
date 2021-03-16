# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.

import logging
from typing import Optional

from dacite import from_dict
from flask import jsonify, make_response, request
from flask_restx import Resource

from txmatching.auth.auth_check import (require_role, require_valid_config_id,
                                        require_valid_txm_event_id)
from txmatching.auth.data_types import UserRole
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigurationJson
from txmatching.data_transfer_objects.external_patient_upload.swagger import \
    FailJson
from txmatching.data_transfer_objects.shared_dto import (IdentifierDTOIn,
                                                         SuccessDTOOut)
from txmatching.data_transfer_objects.shared_swagger import (IdentifierJsonIn,
                                                             SuccessJsonOut)
from txmatching.database.services.config_service import (
    get_configuration_from_db_id_or_latest, set_config_as_default)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.web.api.namespaces import configuration_api

logger = logging.getLogger(__name__)


@configuration_api.route('/<config_id>', methods=['GET'])
class ConfigurationApi(Resource):

    @configuration_api.doc(security='bearer')
    @configuration_api.response(code=200, model=ConfigurationJson,
                                description='Returns the latest matching configuration for the current user.')
    @configuration_api.response(code=401, model=FailJson, description='Authentication failed.')
    @configuration_api.response(code=403, model=FailJson,
                                description='Access denied. You do not have rights to access this endpoint.'
                                )
    @configuration_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    @require_valid_txm_event_id()
    @require_valid_config_id()
    def get(self, txm_event_id: int, config_id: Optional[int]) -> str:
        txm_event = get_txm_event_complete(txm_event_id)
        configuration = get_configuration_from_db_id_or_latest(txm_event=txm_event,
                                                               configuration_db_id=config_id)
        return jsonify(configuration)


@configuration_api.route('/default', methods=['PUT'])
class DefaultConfigurationApi(Resource):

    @configuration_api.doc(
        body=IdentifierJsonIn,
        security='bearer',
        description='Set default configuration id for the txm event.'
    )
    @configuration_api.response(code=200, model=SuccessJsonOut, description='Whether the update was successful')
    @configuration_api.response(code=400, model=FailJson, description='Wrong data format.')
    @configuration_api.response(code=401, model=FailJson, description='Authentication failed.')
    @configuration_api.response(code=403, model=FailJson,
                                description='Access denied. You do not have rights to access this endpoint.')
    @configuration_api.response(code=409, model=FailJson, description='Non-unique patients provided.')
    @configuration_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_role(UserRole.ADMIN)
    @require_valid_txm_event_id()
    def put(self, txm_event_id: int):
        identifier_dto = from_dict(data_class=IdentifierDTOIn, data=request.json)
        set_config_as_default(txm_event_id=txm_event_id, configuration_db_id=identifier_dto.id)
        return make_response(jsonify(SuccessDTOOut(success=True)))
