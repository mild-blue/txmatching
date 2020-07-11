import logging

import flask
from flask import render_template, request, redirect, Blueprint, flash

from kidney_exchange.database.services.save_patients import save_patients
from kidney_exchange.utils.excel_parsing.parse_excel_data import parse_excel_data
from kidney_exchange.web.web_utils.load_patients_utils import is_allowed_file_extension

logger = logging.getLogger(__name__)

functional_api = Blueprint('functional', __name__)


@functional_api.route('/')
def home():
    return render_template("template_main.html")


@functional_api.route('/set_parameters')
def set_parameters():
    return render_template("set_parameters.html")


@functional_api.route('/set_individual')
def set_individual():
    return render_template("set_individual.html")


@functional_api.route('/solve')
def solve():
    return render_template("solve.html")


@functional_api.route('/browse_solutions')
def browse_solutions():
    return render_template("browse_solutions.html")


@functional_api.route('/load-patients', methods=["GET", "POST"])
def upload_xlsx():

    if flask.request.method == 'POST':

        patient_data = request.files['patient_data']
        if patient_data.filename == "":
            logger.warning("No patients file uploaded")
            flash("No patients file uploaded")

            return redirect(request.url)

        if not is_allowed_file_extension(patient_data.filename):
            logger.error(f"{patient_data.filename} is not csv or xlsx file")
            flash("This is not a csv or xlsx file, try again")

            return redirect(request.url)

        parsed_data = parse_excel_data(patient_data)
        save_patients(parsed_data)

        flash("File successfully loaded")

        return redirect(request.url)
    if flask.request.method == 'GET':
        return render_template("load_patients.html")
