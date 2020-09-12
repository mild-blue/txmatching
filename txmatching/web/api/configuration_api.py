# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import jsonify, request
from flask_restx import Resource

from txmatching.config.configuration import Configuration
from txmatching.data_transfer_objects.configuration.configuration_swagger import CONFIGURATION_JSON
from txmatching.database.services.config_service import get_current_configuration, save_configuration_as_current
from txmatching.web.api.namespaces import configuration_api
from txmatching.auth.login_check import login_required

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@configuration_api.route('/', methods=['GET', 'POST'])
class ConfigurationApi(Resource):

    @configuration_api.doc(body=CONFIGURATION_JSON, security='bearer')
    @configuration_api.response(code=200, model=CONFIGURATION_JSON, description='')
    @login_required()
    def post(self):
        configuration = Configuration(**request.json)
        save_configuration_as_current(configuration)
        return jsonify(configuration)

    @configuration_api.doc(security='bearer')
    @configuration_api.response(code=200, model=CONFIGURATION_JSON, description='')
    @login_required()
    def get(self) -> str:
        return jsonify(get_current_configuration())
