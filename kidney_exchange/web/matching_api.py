import logging

import bcrypt
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user

from kidney_exchange.data_transfer_objects.configuration.configuration_to_dto import \
    configuration_to_dto
from kidney_exchange.database.services.app_user_management import \
    get_app_user_by_email
from kidney_exchange.database.services.config_service import \
    get_current_configuration
from kidney_exchange.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from kidney_exchange.solve_service.solve_from_db import solve_from_db
from kidney_exchange.web.functional_api import MATCHINGS_TO_SHOW_TO_VIEWER

logger = logging.getLogger(__name__)

service_api = Blueprint('service', __name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


@service_api.route('/get-matchings', methods=['POST'])
def get_matchings():

    configuration_dto = configuration_to_dto(get_current_configuration())

    selected_exchange_index = request.args.get('selected_exchange_index', 1)

    try:
        latest_matchings_and_score_matrix = get_latest_matchings_and_score_matrix()
    except AssertionError:
        solve_from_db()
        latest_matchings_and_score_matrix = get_latest_matchings_and_score_matrix()

    matchings, score_dict, compatible_blood_dict = latest_matchings_and_score_matrix

    matching_index = int(request.args.get('matching_index', 1))

    if current_user.role == 'VIEWER':
        matchings = matchings[:MATCHINGS_TO_SHOW_TO_VIEWER]
        enable_configuration = False
    else:
        enable_configuration = True

    return render_template('browse_solutions.html',
                           enable_configuration=enable_configuration,
                           matchings=matchings,
                           score_dict=score_dict,
                           selected_exchange_index=selected_exchange_index,
                           configuration=configuration_dto,
                           matching_index=matching_index,
                           compatible_blood_dict=compatible_blood_dict)
