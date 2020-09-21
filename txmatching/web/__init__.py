import logging
from enum import Enum
from importlib import util as importing

import sys
from flask import Flask, send_from_directory, request, abort
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from txmatching.auth import bcrypt
from txmatching.database.db import db
from txmatching.web.api.configuration_api import configuration_api
from txmatching.web.api.dummy_matching_api import dummy_matching_api
from txmatching.web.api.matching_api import matching_api
from txmatching.web.api.namespaces import PATIENT_NAMESPACE, MATCHING_NAMESPACE, \
    USER_NAMESPACE, SERVICE_NAMESPACE, CONFIGURATION_NAMESPACE, REPORTS_NAMESPACE, DUMMY_MATCHING_NAMESPACE
from txmatching.web.api.patient_api import patient_api
from txmatching.web.api.report_api import report_api
from txmatching.web.api.service_api import service_api
from txmatching.web.api.user_api import user_api
from txmatching.web.app_configuration.application_configuration import (
    ApplicationConfiguration, get_application_configuration, get_prop)

LOGIN_MANAGER = None
API_VERSION = '/v1'
DOC_ROUTE = '/doc'
ALWAYS_ALLOWED_ROUTES = [DOC_ROUTE, '/swaggerui', '/swagger.json']
ALLOWED_DUMMY_ROUTES = ALWAYS_ALLOWED_ROUTES + [f'{API_VERSION}/{DUMMY_MATCHING_NAMESPACE}']


class DeploymentType(Enum):
    NORMAL = 'normal'
    DUMMY = 'dummy'


def validate_dummy_routes(route: str):
    """
    Validates route path for dummy configuration.
    If path is not found in dummy paths, error 404 is returned.
    :param route: Route path
    """
    for valid_route in ALLOWED_DUMMY_ROUTES:
        if route.lower().startswith(valid_route.lower()):
            return
    abort(404, 'Not found 3.')


def validate_normal_routes(route: str):
    """
    Validates route path for normal configuration.
    If path is dummy route, error 404 is returned.
    :param route: Route path
    """
    if route.lower().startswith(f'/{DUMMY_MATCHING_NAMESPACE}'.lower()):
        abort(404, 'Not found 1.')


def create_app():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                        stream=sys.stdout)

    app = Flask(__name__)
    # fix for https swagger - see https://github.com/python-restx/flask-restx/issues/58
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_port=1, x_for=1, x_host=1, x_prefix=1)

    # For flask.flash (gives feedback when uploading files)
    app.secret_key = 'secret key'

    def load_local_development_config():
        config_file = 'txmatching.web.local_config'
        if importing.find_spec(config_file):
            app.config.from_object(config_file)
            app.config['IS_LOCAL_DEV'] = True

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
        api.add_namespace(report_api, path=f'{API_VERSION}/{REPORTS_NAMESPACE}')
        api.add_namespace(dummy_matching_api, path=f'{API_VERSION}/{DUMMY_MATCHING_NAMESPACE}')

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

    def enable_route_suppress(deployment_type: str):
        """
        Enables route suppress, i.e., handling of allowed routes by configuration.
        :param deployment_type: Deployment type
        """
        @app.before_request
        def before_request_func():
            if deployment_type == DeploymentType.DUMMY.value:
                validate_dummy_routes(request.path)
            elif deployment_type == DeploymentType.NORMAL.value:
                validate_normal_routes(request.path)

    def enable_cors():
        @app.after_request
        def add_headers(response):
            allowed_origins = {
                'http://localhost:4200',  # localhost development
                'https://127.0.0.1:9090'  # proxy on staging, support for swagger
            }
            origin = request.headers.get('origin')
            if origin in allowed_origins:
                response.headers.add('Access-Control-Allow-Origin', origin)
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            return response

    with app.app_context():
        load_local_development_config()
        application_config = get_application_configuration()
        # use configuration for app
        configure_db(application_config)
        configure_encryption()
        # must be registered before apis
        register_static_proxy()
        # enable route suppressing for dummy API
        enable_route_suppress(get_prop('DEPLOYMENT_TYPE'))
        # enable cors
        enable_cors()
        # finish configuration
        configure_apis()
        return app
