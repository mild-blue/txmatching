import logging

import flask
from flask import render_template, request, redirect, Blueprint, flash, url_for
from flask_login import login_required

from kidney_exchange.config.configuration import configuration_to_dto
from kidney_exchange.database.services.config_service import get_current_configuration
from kidney_exchange.database.services.matching_service import get_latest_matchings_and_score_matrix
from kidney_exchange.database.services.patient_service import save_patients
from kidney_exchange.utils.excel_parsing.parse_excel_data import parse_excel_data
from kidney_exchange.web.web_utils import ui_utils
from kidney_exchange.web.web_utils.load_patients_utils import is_allowed_file_extension

logger = logging.getLogger(__name__)

functional_api = Blueprint('functional', __name__)

UPLOAD_XLSX_FLASH_CATEGORY = "UPLOAD_XLSX"


@functional_api.route('/')
@login_required
def home():
    return redirect(url_for("functional.browse_solutions"))


@functional_api.route('/set-parameters')
@login_required
def set_parameters():
    return render_template("set_parameters.html")


@functional_api.route('/set-individual')
@login_required
def set_individual():
    return render_template("set_individual.html")


@functional_api.route('/solve')
@login_required
def solve():
    return render_template("solve.html")


@functional_api.route('/browse-solutions')
@login_required
def browse_solutions():
    configuration_dto = configuration_to_dto(get_current_configuration())

    selected_exchange_index = request.args.get("selected_exchange_index", 1)
    matchings, score_dict = get_latest_matchings_and_score_matrix()

    matching_index = int(request.args.get("matching_index", 1))

    return render_template("browse_solutions.html",
                           matchings=matchings,
                           score_dict=score_dict,
                           selected_exchange_index=selected_exchange_index,
                           configuration=configuration_dto,
                           ui_utils=ui_utils,
                           matching_index=matching_index)


@functional_api.route('/load-patients', methods=["GET", "POST"])
@login_required
def upload_xlsx():
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
