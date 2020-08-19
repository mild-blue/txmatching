# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging
import os

import bcrypt
from flask import abort, Blueprint
from flask import current_app as app
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import OperationalError

from kidney_exchange.database.db import db
from kidney_exchange.database.services.app_user_management import \
    get_app_user_by_email

logger = logging.getLogger(__name__)

service_api = Namespace('service')
service_blueprint = Blueprint('service', __name__)

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


@service_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('functional.home'))

    if request.method == 'GET':
        return render_template('login.html')

    logger.info(request)
    user = get_app_user_by_email(request.form['username'])
    if user is None:
        logger.warning(f"User {request.form['username']} not found.")
        flash('Invalid credentials', LOGIN_FLASH_CATEGORY)
        return redirect(url_for('service.login'))

    if not bcrypt.checkpw(request.form['password'].encode('utf-8'), user.pass_hash.encode('utf-8')):
        logger.warning(f"Invalid password for user {request.form['username']}.")
        flash('Invalid credentials', LOGIN_FLASH_CATEGORY)
        return redirect(url_for('service.login'))

    user.set_authenticated(True)
    login_user(user)
    logger.info(f"User {request.form['username']} logged in.")
    return redirect(url_for('functional.browse_solutions'))


@service_blueprint.route('/logout')
@login_required
def logout():
    username = current_user.email
    logout_user()
    logger.info(f'User {username} logged out.')
    return redirect(url_for('functional.home'))


# TODO Improve this https://trello.com/c/pKMqnv7X
def check_admin(role: str):
    if role != 'ADMIN':
        abort(403)


def check_admin_or_editor(role: str):
    if role not in {'ADMIN', 'EDITOR'}:
        abort(403)
