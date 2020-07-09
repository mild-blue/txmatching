import logging
import os
import sys
import traceback

from flask import Flask, render_template, request, redirect

from kidney_exchange.database.db import db
from kidney_exchange.web.version_api import version_api


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# register blueprints
app.register_blueprint(version_api)


def configure_db():
    # TODO load configuration from file and override it with env - to discussion with team
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    url = os.environ.get("POSTGRES_URL")
    po_db = os.environ.get("POSTGRES_DB")

    app.config['SQLALCHEMY_DATABASE_URI'] \
        = f'postgresql+psycopg2://{user}:{password}@{url}/{po_db}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


with app.app_context():
    configure_db()


app.config["CSV_UPLOADS"] = "kidney_exchange/web/csv_uploads"
app.config["ALLOWED_CSV_EXTENSIONS"] == ["CSV", "XLSX"]

def allowed_csv(filename):
    ext = filename.split(".")[1]
    if ext.upper() in app.config["ALLOWED_CSV_EXTENSIONS"]:
        return True
    else:
        return False

@app.route('/load-patients', methods=["GET", "POST"])
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


if __name__ == '__main__':
    app.run(debug=True)
