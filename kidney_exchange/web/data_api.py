import logging

import flask
from flask import request, Blueprint

from kidney_exchange.config.configuration import configuration_to_dto, configuration_from_dto
from kidney_exchange.database.services.config_service import save_configuration_as_current, get_current_configuration
from kidney_exchange.solvers.solve_from_config import solve_from_db

logger = logging.getLogger(__name__)

data_api = Blueprint('data', __name__)


@data_api.route('/configuration', methods=["GET", "POST"])
def save_and_get_configuration():
    if flask.request.method == 'POST':
        configuration = configuration_from_dto(request.json)
        save_configuration_as_current(configuration)
        return "Successfully saved configuration"

    elif flask.request.method == 'GET':
        return configuration_to_dto(get_current_configuration())


@data_api.route('/run_solver', methods=["GET"])
def run_solver():
    solve_from_db()
    return "Success"
