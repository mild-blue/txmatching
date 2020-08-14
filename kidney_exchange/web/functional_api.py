import logging

import flask
from flask import render_template, request, redirect, Blueprint, flash, url_for
from flask_login import login_required, current_user

from kidney_exchange.database.services.config_service import get_current_configuration
from kidney_exchange.database.services.matching_service import get_latest_matchings_and_score_matrix
from kidney_exchange.database.services.patient_service import save_patients
from kidney_exchange.solve_service.solve_from_db import solve_from_db
from kidney_exchange.utils.excel_parsing.parse_excel_data import parse_excel_data
from kidney_exchange.data_transfer_objects.configuration.configuration_to_dto import configuration_to_dto
from kidney_exchange.web.service_api import check_admin
from kidney_exchange.web.web_utils.load_patients_utils import is_allowed_file_extension

logger = logging.getLogger(__name__)

functional_api = Blueprint('functional', __name__)

UPLOAD_XLSX_FLASH_CATEGORY = "UPLOAD_XLSX"
MATCHINGS_TO_SHOW_TO_VIEWER = 5


@functional_api.route('/')
@login_required
def home():
    return redirect(url_for("functional.browse_solutions"))


@functional_api.route('/browse-solutions')
@login_required
def browse_solutions():
    configuration_dto = configuration_to_dto(get_current_configuration())

    selected_exchange_index = request.args.get("selected_exchange_index", 1)

    try:
        latest_matchings_and_score_matrix = get_latest_matchings_and_score_matrix()
    except AssertionError:
        solve_from_db()
        latest_matchings_and_score_matrix = get_latest_matchings_and_score_matrix()

    matchings, score_dict, compatible_blood_dict = latest_matchings_and_score_matrix

    matching_index = int(request.args.get("matching_index", 1))

    if current_user.role == 'VIEWER':
        matchings = matchings[:MATCHINGS_TO_SHOW_TO_VIEWER]
        enable_configuration = False
    else:
        enable_configuration = True

    return render_template("browse_solutions.html",
                           enable_configuration=enable_configuration,
                           matchings=matchings,
                           score_dict=score_dict,
                           selected_exchange_index=selected_exchange_index,
                           configuration=configuration_dto,
                           matching_index=matching_index,
                           compatible_blood_dict=compatible_blood_dict)


@functional_api.route('/load-patients', methods=["GET", "POST"])
@login_required
def upload_xlsx():
    check_admin(current_user.role)
    if flask.request.method == 'POST':

        patient_data = request.files['patient_data']
        if patient_data.filename == "":
            logger.warning("No patients file uploaded")
            flash("No patients file uploaded", UPLOAD_XLSX_FLASH_CATEGORY)

            return redirect(request.url)

        if not is_allowed_file_extension(patient_data.filename):
            logger.error(f"{patient_data.filename} is not csv or xlsx file")
            flash("This is not a csv or xlsx file, try again", UPLOAD_XLSX_FLASH_CATEGORY)

            return redirect(request.url)

        parsed_data = parse_excel_data(patient_data)
        save_patients(parsed_data)

        flash("File successfully loaded", UPLOAD_XLSX_FLASH_CATEGORY)

        return redirect(request.url)
    elif flask.request.method == 'GET':
        return render_template("load_patients.html")
