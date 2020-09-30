# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import jsonify
from flask_restx import Resource

from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigurationJson
from txmatching.database.services.config_service import \
    get_current_configuration
from txmatching.utils.logged_user import get_current_user
from txmatching.web.api.namespaces import configuration_api

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@configuration_api.route('/', methods=['GET', 'POST'])
class ConfigurationApi(Resource):

    @configuration_api.doc(security='bearer')
    @configuration_api.response(code=200, model=ConfigurationJson, description='')
    @require_user_login()
    def get(self) -> str:
        current_user = get_current_user()
        return jsonify(get_current_configuration(current_user.default_txm_event_id))
