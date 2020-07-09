import logging
import os
import sys

from flask import Flask, render_template

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


@app.route('/')
def home():
    return load_patients()


@app.route('/load_patients')
def load_patients():
    return render_template("load_patients.html")


@app.route('/set_parameters')
def set_parameters():
    return render_template("set_parameters.html")


@app.route('/set_individual')
def set_individual():
    return render_template("set_individual.html")


@app.route('/solve')
def solve():
    return render_template("solve.html")


@app.route('/browse_solutions')
def browse_solutions():
    return render_template("browse_solutions.html")


if __name__ == '__main__':
    app.run(debug=True)
