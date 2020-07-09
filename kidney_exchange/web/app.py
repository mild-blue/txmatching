import logging
import os
import sys
from importlib import util as importing

from flask import Flask, render_template

from kidney_exchange.database.db import db
from kidney_exchange.web.service_api import service_api

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# register blueprints
app.register_blueprint(service_api)


def load_local_development_config():
    config_file = 'kidney_exchange.web.local_config'
    if importing.find_spec(config_file):
        app.config.from_object(config_file)


def configure_db():
    # TODO load configuration from file and override it with env - to discussion with team
    # https://trello.com/c/OXeSTk75/96-vymyslet-a-pridat-nejaky-rozumny-zpsov-jak-nahravat-konfiguraci-connection-strings-napr-aplikace
    user = os.environ.get("POSTGRES_USER", app.config.get("POSTGRES_USER"))
    password = os.environ.get("POSTGRES_PASSWORD", app.config.get("POSTGRES_PASSWORD"))
    url = os.environ.get("POSTGRES_URL", app.config.get("POSTGRES_URL"))
    po_db = os.environ.get("POSTGRES_DB", app.config.get("POSTGRES_DB"))

    app.config['SQLALCHEMY_DATABASE_URI'] \
        = f'postgresql+psycopg2://{user}:{password}@{url}/{po_db}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


with app.app_context():
    load_local_development_config()
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

    app.run(host='localhost', port=8080, debug=True)
