import logging

from flask import render_template, request, redirect, Blueprint, flash

from kidney_exchange.web.web_utils.load_patients_utils import is_allowed_file_extension

logger = logging.getLogger(__name__)

functional_api = Blueprint('functional', __name__)


@functional_api.route('/')
def home():
    return render_template("template_main.html")


@functional_api.route('/load_patients')
def load_patients():
    return render_template("load_patients.html")


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
def upload_csv():
    if request.files:
        uploaded_csv = request.files["csv"]
        if uploaded_csv.filename == "":
            logger.warning("No patients file uploaded")
            flash("No patients file uploaded")

            return redirect(request.url)

        if not is_allowed_file_extension(uploaded_csv.filename):
            logger.error(f"{uploaded_csv.filename} is not csv or xlsx file")
            flash("This is not a csv or xlsx file, try again")

            return redirect(request.url)

        flash("File successfully loaded")

        return redirect(request.url)

    return render_template("load_patients.html")
