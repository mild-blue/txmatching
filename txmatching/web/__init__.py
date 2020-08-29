import logging
import sys
from importlib import util as importing

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from txmatching.database.db import db
from txmatching.web.api.configuration_api import configuration_api
from txmatching.web.api.matching_api import matching_api
from txmatching.web.api.namespaces import PATIENT_NAMESPACE, MATCHING_NAMESPACE, \
    USER_NAMESPACE, SERVICE_NAMESPACE, CONFIGURATION_NAMESPACE
from txmatching.web.api.patient_api import patient_api
from txmatching.web.api.service_api import service_api
from txmatching.web.api.user_api import user_api
from txmatching.web.app_configuration.application_configuration import (
    ApplicationConfiguration, get_application_configuration)
from txmatching.web.auth import bcrypt

LOGIN_MANAGER = None
API_VERSION = '/v1'


def create_app():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                        stream=sys.stdout)

    app = Flask(__name__)
    # enable cors for localhost development
    CORS(app, resources={rf'/${API_VERSION}/*': {'origins': ['http://localhost:4200']}}, supports_credentials=True)
    # fix for https swagger - see https://github.com/python-restx/flask-restx/issues/58
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_port=1, x_for=1, x_host=1, x_prefix=1)

    # For flask.flash (gives feedback when uploading files)
    app.secret_key = 'secret key'

    def load_local_development_config():
        config_file = 'txmatching.web.local_config'
        if importing.find_spec(config_file):
            app.config.from_object(config_file)

    def configure_db(application_config: ApplicationConfiguration):
        app.config['SQLALCHEMY_DATABASE_URI'] \
            = f'postgresql+psycopg2://' \
              f'{application_config.postgres_user}:{application_config.postgres_password}@' \
              f'{application_config.postgres_url}/{application_config.postgres_db}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

    def configure_encryption():
        bcrypt.init_app(app)

    def configure_apis():
        # Set up Swagger and API
        authorizations = {
            'bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            }
        }

        api = Api(app, authorizations=authorizations, doc='/doc/')
        api.add_namespace(user_api, path=f'{API_VERSION}/{USER_NAMESPACE}')
        api.add_namespace(service_api, path=f'{API_VERSION}/{SERVICE_NAMESPACE}')
        api.add_namespace(matching_api, path=f'{API_VERSION}/{MATCHING_NAMESPACE}')
        api.add_namespace(patient_api, path=f'{API_VERSION}/{PATIENT_NAMESPACE}')
        api.add_namespace(configuration_api, path=f'{API_VERSION}/{CONFIGURATION_NAMESPACE}')

    # pylint: disable=unused-variable
    # routes registered in flask
    def register_static_proxy():
        # serving main html which then asks for all javascript
        @app.route('/')
        def index_html():
            return send_from_directory('frontend/dist/frontend', 'index.html')

        # used only if the there's no other endpoint registered
        # we need it to load static resources for the frontend
        @app.route('/<path:path>', methods=['GET'])
        def static_proxy(path):
            return send_from_directory('frontend/dist/frontend', path)

    with app.app_context():
        load_local_development_config()
        application_config = get_application_configuration()
        configure_db(application_config)
        configure_encryption()
        register_static_proxy()  # must be registered before apis
        configure_apis()
        return app
