import logging
import os
import sys
from importlib import util as importing

import flask_login
from flask import Flask

from kidney_exchange.database.db import db
from kidney_exchange.database.services.app_user_management import get_app_user_by_email
from kidney_exchange.web.data_api import data_api
from kidney_exchange.web.functional_api import functional_api
from kidney_exchange.web.service_api import service_api

login_manager = None


def create_app():
    logging.basicConfig(level=logging.DEBUG,
                       format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                       stream=sys.stdout)

    app = Flask(__name__)

    # register blueprints
    app.register_blueprint(service_api)
    app.register_blueprint(functional_api)
    app.register_blueprint(data_api)

    # For flask.flash (gives feedback when uploading files)
    app.secret_key = "secret key"

    # Add config
    app.config["CSV_UPLOADS"] = "kidney_exchange/web/csv_uploads"
    app.config["ALLOWED_FILE_EXTENSIONS"] = ["CSV", "XLSX"]

    global login_manager
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "service.login"

    @login_manager.user_loader
    def user_loader(user_id):
        return get_app_user_by_email(user_id)

    def load_local_development_config():
        config_file = 'kidney_exchange.web.local_config'
        if importing.find_spec(config_file):
            app.config.from_object(config_file)

    def configure_db():
        # TODO load configuration from file and override it with env - to discussion with team https://trello.com/c/OXeSTk75/
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
        return app
