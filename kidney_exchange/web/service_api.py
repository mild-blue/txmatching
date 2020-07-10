import logging
import os

from flask import jsonify, g, render_template, request, redirect, Blueprint, current_app as app
from sqlalchemy.exc import OperationalError

from kidney_exchange.database.db import db

logger = logging.getLogger(__name__)

service_api = Blueprint('service', __name__)


@service_api.route("/db-health")
def database_health_check():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok'})
    except OperationalError as ex:
        logger.exception(f'Connection to database is not working.')
        return jsonify({'status': 'error', 'exception': ex.args[0]}), 503


@service_api.route('/')
def home():
    return render_template("template_main.html")


@service_api.route('/load_patients')
def load_patients():
    return render_template("load_patients.html")


@service_api.route('/set_parameters')
def set_parameters():
    return render_template("set_parameters.html")


@service_api.route('/set_individual')
def set_individual():
    return render_template("set_individual.html")


@service_api.route('/solve')
def solve():
    return render_template("solve.html")


@service_api.route('/browse_solutions')
def browse_solutions():
    return render_template("browse_solutions.html")


app.config["CSV_UPLOADS"] = "kidney_exchange/web/csv_uploads"
app.config["ALLOWED_CSV_EXTENSIONS"] = ["CSV", "XLSX"]


def allowed_csv(filename):
    ext = filename.split(".")[1]
    if ext.upper() in app.config["ALLOWED_CSV_EXTENSIONS"]:
        return True
    else:
        return False


@service_api.route('/load-patients', methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        if request.files:
            uploaded_csv = request.files["csv"]
            uploaded_csv.save(os.path.join(app.config["CSV_UPLOADS"], uploaded_csv.filename))
            if not allowed_csv(uploaded_csv.filename):
                print("[WARN] Uploaded file is not .csv or .xlsx")

                return redirect(request.url)

            return redirect(request.url)

    return render_template("load_patients.html")


@service_api.route("/version")
def version_route():
    return jsonify({'version': get_version()})


def get_version() -> str:
    """
    Retrieves version from the flask app.
    """
    if 'version' not in g:
        g.version = read_version('development')

    return g.version


def read_version(default: str) -> str:
    """
    Reads version from the file or returns default version.
    """
    file_path = os.environ.get('RELEASE_FILE_PATH')
    file_path = file_path if file_path else app.config.get('RELEASE_FILE_PATH')
    logger.debug(f'File path: {file_path}')

    version = None
    if file_path:
        with open(file_path, 'r') as file:
            version = file.readline().strip()
            logger.info(f'Settings version as: {version}')

    return version if version else default