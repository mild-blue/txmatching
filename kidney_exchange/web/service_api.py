import logging
import os

import bcrypt
from flask import Blueprint, abort
from flask import current_app as app
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import OperationalError

from kidney_exchange.database.db import db
from kidney_exchange.database.services.app_user_management import \
    get_app_user_by_email

logger = logging.getLogger(__name__)

service_api = Blueprint('service', __name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


@service_api.route('/db-health')
def database_health_check():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok'})
    except OperationalError as ex:
        logger.exception('Connection to database is not working.')
        return jsonify({'status': 'error', 'exception': ex.args[0]}), 503


@service_api.route('/version')
def version_route():
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


@service_api.route('/login', methods=['GET', 'POST'])
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


@service_api.route('/logout')
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
