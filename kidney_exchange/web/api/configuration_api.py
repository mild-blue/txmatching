import logging

from flask import jsonify, request
from flask_restx import Resource

from kidney_exchange.data_transfer_objects.configuration.configuration_from_dto import configuration_from_dto
from kidney_exchange.data_transfer_objects.configuration.configuration_swagger import CONFIGURATION_MODEL
from kidney_exchange.data_transfer_objects.configuration.configuration_to_dto import configuration_to_dto
from kidney_exchange.database.services.config_service import get_current_configuration, save_configuration_as_current
from kidney_exchange.web.api.namespaces import configuration_api

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@configuration_api.route('/', methods=['GET', 'POST'])
class Configuration(Resource):

    @configuration_api.doc(body=CONFIGURATION_MODEL)
    @configuration_api.response(code=200, model=CONFIGURATION_MODEL, description="")
    def post(self):
        configuration = configuration_from_dto(request.json)
        save_configuration_as_current(configuration)
        return jsonify(configuration)

    @configuration_api.response(code=200, model=CONFIGURATION_MODEL, description="")
    def get(self) -> str:
        configuration_dto = configuration_to_dto(get_current_configuration())
        return jsonify(configuration_dto)
