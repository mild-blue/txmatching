# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging

from flask import jsonify
from flask_restx import Resource, fields
from sqlalchemy.exc import OperationalError

from txmatching.configuration.app_configuration.application_configuration import (
    ApplicationEnvironment, get_application_configuration)
from txmatching.data_transfer_objects.shared_swagger import FailJson
from txmatching.database.db import db
from txmatching.web.web_utils.namespaces import service_api
from txmatching.web.web_utils.route_utils import response_ok

logger = logging.getLogger(__name__)


@service_api.route('/status', methods=['GET'])
class Status(Resource):
    status = service_api.model('ServiceStatus', {
        'status': fields.String(required=True, description='Indication of service\'s health.', enum=['OK', 'Failing']),
        'exception': fields.String(required=False, description='Additional indication what is wrong.')
    })

    @service_api.response_ok(status, description='Returns ok if the service is healthy.')
    @service_api.response_error_unexpected(FailJson)
    @service_api.response_error_services_failing(FailJson)
    def get(self):
        try:
            db.session.execute('SELECT 1')
            return response_ok({'status': 'ok'})
        except OperationalError as ex:
            logger.exception('Connection to database is not working.')
            return {'status': 'error', 'detail': ex.args[0]}, 503


@service_api.route('/version', methods=['GET'])
class Version(Resource):
    version_model = service_api.model('Version', {
        'version': fields.String(required=True, description='Version of the running code.'),
        'environment': fields.String(required=True,
                                     enum=[env.value for env in ApplicationEnvironment],
                                     description='Environment the code was build for.')
    })

    @service_api.response_ok(version_model, description='Returns version of the code')
    @service_api.response_error_unexpected(FailJson)
    def get(self):
        conf = get_application_configuration()
        logger.debug(f'Application version: {conf.code_version} in environment {conf.environment}.')
        return jsonify({'version': conf.code_version, 'environment': conf.environment})
