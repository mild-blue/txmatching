# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import jsonify
from flask_restx import Resource

from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigurationJson
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    FailJson
from txmatching.database.services.config_service import \
    latest_configuration_for_txm_event
from txmatching.database.services.txm_event_service import \
    get_txm_event_id_for_current_user
from txmatching.web.api.namespaces import configuration_api

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@configuration_api.route('/', methods=['GET', 'POST'])
class ConfigurationApi(Resource):

    @configuration_api.doc(security='bearer')
    @configuration_api.response(code=200, model=ConfigurationJson, description='Matching configuration.')
    @configuration_api.response(code=401, model=FailJson, description='Authentication failed.')
    @configuration_api.response(
        code=403,
        model=FailJson,
        description='Access denied. You do not have rights to access this endpoint.'
    )
    @configuration_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def get(self) -> str:
        return jsonify(latest_configuration_for_txm_event(get_txm_event_id_for_current_user()))
