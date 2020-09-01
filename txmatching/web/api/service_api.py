# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging
import os

from flask import current_app as app
from flask import jsonify
from flask_restx import Resource, fields
from sqlalchemy.exc import OperationalError

from txmatching.database.db import db
from txmatching.web.api.namespaces import service_api

logger = logging.getLogger(__name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


@service_api.route('/status', methods=['GET'])
class Status(Resource):
    status = service_api.model('ServiceStatus', {
        'status': fields.String(required=True, description='Indication of service\'s health.', enum=['OK', 'Failing']),
        'exception': fields.String(required=False, description='Additional indication what is wrong.')
    })

    @service_api.response(code=200, model=status, description='Returns ok if service is healthy.')
    @service_api.response(code=503, model=status, description='Some services are failing.')
    def get(self):
        try:
            db.session.execute('SELECT 1')
            return {'status': 'ok'}
        except OperationalError as ex:
            logger.exception('Connection to database is not working.')
            return {'status': 'error', 'exception': ex.args[0]}, 503


@service_api.route('/version', methods=['GET'])
class Version(Resource):
    version_model = service_api.model('Version', {
        'version': fields.String(required=True, description='Version of the running code.')
    })

    @service_api.response(code=200, model=version_model, description='Returns version of the code')
    def get(self):
        version = get_version()
        logger.debug(f'Responding on version endpoint with version {version}')
        return jsonify({'version': get_version()})


def get_version() -> str:
    """
    Retrieves version from the flask app.
    """
    return read_version('development')


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
