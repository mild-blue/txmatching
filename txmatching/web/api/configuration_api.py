# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.user.user_auth_check import require_user_login, require_user_edit_access
from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.configuration.configuration_swagger import ConfigurationJson
from txmatching.database.services.config_service import get_current_configuration, save_configuration_as_current
from txmatching.web.api.namespaces import configuration_api

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@configuration_api.route('/', methods=['GET', 'POST'])
class ConfigurationApi(Resource):

    @configuration_api.doc(body=ConfigurationJson, security='bearer')
    @configuration_api.response(code=200, model=ConfigurationJson, description='')
    @require_user_edit_access()
    def post(self):
        configuration = Configuration(**request.json)
        save_configuration_as_current(configuration)
        return jsonify(configuration)

    @configuration_api.doc(security='bearer')
    @configuration_api.response(code=200, model=ConfigurationJson, description='')
    @require_user_login()
    def get(self) -> str:
        return jsonify(get_current_configuration())
