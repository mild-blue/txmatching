import logging

import flask
from flask import request, Blueprint

from kidney_exchange.config.configuration import configuration_to_dto, configuration_from_dto
from kidney_exchange.database.services.config_service import save_configuration_as_current, get_current_configuration

logger = logging.getLogger(__name__)

data_api = Blueprint('data', __name__)


@data_api.route('/config', methods=["GET", "POST"])
def rest_config():
    if flask.request.method == 'POST':
        configuration = configuration_from_dto(**request.json)
        save_configuration_as_current(configuration)
        return "Successfully saved configuration"

    elif flask.request.method == 'GET':
        return configuration_to_dto(get_current_configuration())
