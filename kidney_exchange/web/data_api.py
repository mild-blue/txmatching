import dataclasses
import logging

import flask
from flask import request, Blueprint

from kidney_exchange.config import ConfigurationDto
from kidney_exchange.database.services.config_service import save_configuration_as_current, get_current_configuration

logger = logging.getLogger(__name__)

data_api = Blueprint('data', __name__)


@data_api.route('/config', methods=["GET", "POST"])
def rest_config():
    if flask.request.method == 'POST':
        configuration_dto = ConfigurationDto(**request.json)
        save_configuration_as_current(configuration_dto.from_dto())
        return "Successfully saved configuration"

    elif flask.request.method == 'GET':
        return dataclasses.asdict(get_current_configuration().to_dto())
