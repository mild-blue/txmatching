import logging

import flask
from flask import request, Blueprint, redirect
from flask_login import current_user, login_required

from txmatching.data_transfer_objects.configuration.configuration_from_dto import configuration_from_dto
from txmatching.data_transfer_objects.configuration.configuration_to_dto import configuration_to_dto
from txmatching.database.services.config_service import save_configuration_as_current, get_current_configuration
from txmatching.database.services.scorer_service import calculate_current_score_matrix
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.web.api.service_api import check_admin_or_editor

logger = logging.getLogger(__name__)

data_api = Blueprint('data', __name__)


@data_api.route('/configuration', methods=["GET", "POST"])
@login_required
def save_and_get_configuration():
    check_admin_or_editor(current_user.role)
    if flask.request.method == 'POST':
        configuration = configuration_from_dto(request.form)
        save_configuration_as_current(configuration)
        solve_from_db()
        return redirect("/browse-solutions")

    elif flask.request.method == 'GET':
        return configuration_to_dto(get_current_configuration())


@data_api.route('/run_solver', methods=["GET"])
@login_required
def run_solver():
    check_admin_or_editor(current_user.role)
    solve_from_db()
    return "Success"


@data_api.route('/run_scorer', methods=["GET"])
@login_required
def run_scorer():
    check_admin_or_editor(current_user.role)
    score_matrix = calculate_current_score_matrix()
    return score_matrix
