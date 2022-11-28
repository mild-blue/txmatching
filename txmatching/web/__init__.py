import logging
import os
import re
import time
import uuid
from importlib import util as importing
from typing import List, Tuple

import sentry_sdk
from flask import Flask, make_response, request, send_from_directory
from flask_restx import Api
from flask_restx.apidoc import ui_for
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.middleware.proxy_fix import ProxyFix

from txmatching.auth.crypto import bcrypt
from txmatching.configuration.app_configuration.application_configuration import (
    ApplicationConfiguration, ApplicationEnvironment,
    build_db_connection_string, get_application_configuration)
from txmatching.database.db import db
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web.api.configuration_api import configuration_api
from txmatching.web.api.matching_api import matching_api
from txmatching.web.api.optimizer_api import optimizer_api
from txmatching.web.api.patient_api import patient_api
from txmatching.web.api.public_api import public_api
from txmatching.web.api.report_api import report_api
from txmatching.web.api.service_api import service_api
from txmatching.web.api.txm_event_api import txm_event_api
from txmatching.web.api.user_api import user_api
from txmatching.web.error_handler import register_error_handlers
from txmatching.web.web_utils.logging_config import setup_logging
from txmatching.web.web_utils.namespaces import (CONFIGURATION_NAMESPACE,
                                                 MATCHING_NAMESPACE,
                                                 OPTIMIZER_NAMESPACE,
                                                 PATIENT_NAMESPACE,
                                                 PUBLIC_NAMESPACE,
                                                 REPORTS_NAMESPACE,
                                                 SERVICE_NAMESPACE,
                                                 TXM_EVENT_NAMESPACE,
                                                 USER_NAMESPACE, enums_api)

LOGIN_MANAGER = None
API_VERSION = '/v1'
SWAGGER_URL = 'doc'
logger = logging.getLogger(__name__)
VERSION = '0.3'
SWAGGER_TITLE = 'TXMatching API'
SWAGGER_FOLDER = 'swagger'
SWAGGER_FOLDER_PATH = 'txmatching/web/swagger/'
SWAGGER = 'swagger.json'
SWAGGER_YAML = 'swagger.yaml'
SWAGGER_PUBLIC = 'swagger_public.json'
PATH_TO_SWAGGER_JSON = get_absolute_path(f'{SWAGGER_FOLDER_PATH}{SWAGGER}')
PATH_TO_SWAGGER_YAML = get_absolute_path(f'{SWAGGER_FOLDER_PATH}{SWAGGER_YAML}')
PATH_TO_PUBLIC_SWAGGER_JSON = get_absolute_path(f'{SWAGGER_FOLDER_PATH}{SWAGGER_PUBLIC}')
AUTHORIZATIONS = {
    'bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}


class ApiWithProvidedSpecsUrl(Api):
    def __init__(self, specs_url: str, **kwargs):
        super().__init__(**kwargs)
        self._specs_url = specs_url

    @property
    def specs_url(self):
        return self._specs_url


class RequestPerformance:
    def __init__(self, log_queries):
        self._log_queries = log_queries
        self._sql_queries: List[Tuple[str, float]] = []
        self._sql_start_time = 0.0
        self._sql_total_time = 0.0
        self._request_start_time = time.perf_counter()
        self._request_total_time = 0.0
        self._request_id = None
        self._user_ip = None

        # pylint: disable=too-many-arguments,unused-argument,unused-variable
        @event.listens_for(Engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            self._sql_start_time = time.perf_counter()

        # pylint: disable=too-many-arguments,unused-argument,unused-variable
        @event.listens_for(Engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            now = time.perf_counter()
            last_execution_duration = now - self._sql_start_time
            self._sql_total_time += last_execution_duration

            self._add_sql_query(statement, last_execution_duration)

    def _add_sql_query(self, query, duration) -> None:
        query_simplified = re.sub(r'SELECT.*\sFROM', 'SELECT * FROM', str(query))
        self._sql_queries.append((query_simplified, duration))

        if self._log_queries:
            logger.debug(f'SQL query ({duration:.6f}s): {query_simplified}')

    def start(self) -> None:
        self._sql_queries = []
        self._sql_start_time = 0.0
        self._sql_total_time = 0.0
        self._request_start_time = time.perf_counter()
        self._request_total_time = 0.0
        self._request_id = uuid.uuid4()
        self._user_ip = request.remote_addr
        logger.info(f'User {self._user_ip}: Request {self._request_id} started.')

    def finish(self) -> None:
        now = time.perf_counter()
        request_duration = int((now - self._request_start_time) * 1000)
        self._request_total_time += request_duration
        logger.info(f'User {self._user_ip}: Request {self._request_id} took {int(self._request_total_time)} ms. '
                    f'Method: {request.method} {request.path}, arguments: {dict(request.args)}. '
                    f'SQL Queries: {len(self._sql_queries)}, SQL total time: {int(self._sql_total_time * 1000)} ms.')


# pylint: disable=too-many-statements
def create_app() -> Flask:
    setup_logging()

    app = Flask(__name__,
                static_folder='swagger',
                template_folder='templates',
                static_url_path=f'/{SWAGGER_FOLDER}'
                )
    # fix for https swagger - see https://github.com/python-restx/flask-restx/issues/58
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_port=1, x_for=1, x_host=1, x_prefix=1)

    # For flask.flash (gives feedback when uploading files)
    app.secret_key = 'secret key'

    def init_sentry(application_configuration: ApplicationConfiguration):
        dsn = application_configuration.sentry_dsn
        if dsn:
            sentry_sdk.init(
                dsn=dsn,
                integrations=[FlaskIntegration()],

                # Set traces_sample_rate to 1.0 to capture 100%
                # of transactions for performance monitoring.
                # We recommend adjusting this value in production.
                traces_sample_rate=1.0,

                # By default the SDK will try to use the SENTRY_RELEASE
                # environment variable, or infer a git commit
                # SHA as release, however you may want to set
                # something more human-readable.
                # release="myapp@1.0.0",
            )

    def load_local_development_config():
        config_file = 'txmatching.local_config'
        if importing.find_spec(config_file):
            app.config.from_object(config_file)
            app.config['IS_LOCAL_DEV'] = True

    def configure_db(application_configuration: ApplicationConfiguration):
        app.config['SQLALCHEMY_DATABASE_URI'] \
            = build_db_connection_string(
            application_configuration.postgres_user,
            application_configuration.postgres_password,
            application_configuration.postgres_url,
            application_configuration.postgres_db
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

    def configure_encryption():
        bcrypt.init_app(app)

    def configure_apis(application_configuration: ApplicationConfiguration):
        # disable default error handling
        app.config['ERROR_INCLUDE_MESSAGE'] = False

        # Set up Swagger and API

        full_swagger = application_configuration.environment != ApplicationEnvironment.PRODUCTION
        if full_swagger:
            specs_url = f'/{SWAGGER_FOLDER}/{SWAGGER}'
        else:
            # only limited swagger when we're running in the production
            # specs_url = f'/{SWAGGER_FOLDER}/{SWAGGER_PUBLIC}'
            # for the moment we show the full swagger always as not everything is possible to do via FE.

            specs_url = f'/{SWAGGER_FOLDER}/{SWAGGER}'

        api = ApiWithProvidedSpecsUrl(
            authorizations=AUTHORIZATIONS,
            version=VERSION,
            title=SWAGGER_TITLE,
            specs_url=specs_url
        )

        def generate_docs():
            response = make_response(ui_for(api))
            response.headers['Content-Security-Policy'] = "default-src 'self'; connect-src 'self'; media-src data:;" \
                                                          "img-src 'self' data:; style-src 'self' 'unsafe-inline'; " \
                                                          "script-src 'self' 'unsafe-inline'"
            return response

        app.add_url_rule(f'/{SWAGGER_URL}/', view_func=generate_docs)
        api.init_app(app, add_specs=False)
        add_all_namespaces(api)

        register_error_handlers(api)

    # pylint: disable=unused-variable
    # routes registered in flask
    def register_static_proxy():
        # serving main html which then asks for all javascript
        @app.route('/')
        def index_html():
            response = send_from_directory('frontend/dist/frontend', 'index.html')
            # prevent clickjacking
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            return response

        # used only if the there's no other endpoint registered
        # we need it to load static resources for the frontend
        @app.route('/<path:path>', methods=['GET'])
        def static_proxy(path):
            response = send_from_directory('frontend/dist/frontend', path)
            # prevent clickjacking
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            return response

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
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
            return response

    def log_request_performance():
        # Set log_queries=True to log sql queries with duration
        request_performance = RequestPerformance(log_queries=False)

        @app.before_request
        def before_request_callback():
            if os.getenv('SHOW_USERS_ACTIONS') != 'true':
                return
            request_performance.start()

        @app.after_request
        def after_request_callback(response):
            if os.getenv('SHOW_USERS_ACTIONS') != 'true':
                return response
            request_performance.finish()
            return response

    with app.app_context():
        load_local_development_config()
        application_config = get_application_configuration()
        init_sentry(application_config)
        # use configuration for app
        configure_db(application_config)
        configure_encryption()
        # must be registered before apis
        register_static_proxy()
        # enable cors
        enable_cors()
        # performance_stats
        log_request_performance()
        # finish configuration
        configure_apis(application_config)
        return app


def add_public_namespaces(api: Api):
    api.add_namespace(public_api, path=f'{API_VERSION}/{PUBLIC_NAMESPACE}')
    api.add_namespace(user_api, path=f'{API_VERSION}/{USER_NAMESPACE}')
    api.add_namespace(service_api, path=f'{API_VERSION}/{SERVICE_NAMESPACE}')
    api.add_namespace(enums_api)
    api.add_namespace(optimizer_api, path=f'{API_VERSION}/{OPTIMIZER_NAMESPACE}')


def add_all_namespaces(api: Api):
    add_public_namespaces(api)
    api.add_namespace(matching_api,
                      path=f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/<int:txm_event_id>/{MATCHING_NAMESPACE}')
    api.add_namespace(patient_api,
                      path=f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/<int:txm_event_id>/{PATIENT_NAMESPACE}')
    api.add_namespace(configuration_api,
                      path=f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/<int:txm_event_id>/{CONFIGURATION_NAMESPACE}')
    api.add_namespace(report_api,
                      path=f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/<int:txm_event_id>/{REPORTS_NAMESPACE}')
    api.add_namespace(txm_event_api, path=f'{API_VERSION}/{TXM_EVENT_NAMESPACE}')
