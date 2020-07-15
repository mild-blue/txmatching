import logging

import flask
from flask import request, Blueprint, redirect

from kidney_exchange.config.configuration import configuration_to_dto, configuration_from_dto
from kidney_exchange.database.services.config_service import save_configuration_as_current, get_current_configuration
from kidney_exchange.database.services.scorer_service import calculate_current_score_matrix
from kidney_exchange.solvers.solve_from_config import solve_from_db

logger = logging.getLogger(__name__)

data_api = Blueprint('data', __name__)


@data_api.route('/configuration', methods=["GET", "POST"])
def save_and_get_configuration():
    if flask.request.method == 'POST':
        configuration = configuration_from_dto(request.form)
        save_configuration_as_current(configuration)
        solve_from_db()
        return redirect("/browse-solutions")

    elif flask.request.method == 'GET':
        return configuration_to_dto(get_current_configuration())


@data_api.route('/run_solver', methods=["GET"])
def run_solver():
    solve_from_db()
    return "Success"


@data_api.route('/run_scorer', methods=["GET"])
def run_scorer():
    score_matrix = calculate_current_score_matrix()
    return score_matrix
