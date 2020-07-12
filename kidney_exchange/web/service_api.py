import logging
import os

import bcrypt
from flask import jsonify, g, Blueprint, current_app as app, render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import OperationalError

from kidney_exchange.database.db import db
from kidney_exchange.database.services.app_user_management import get_app_user_by_email

logger = logging.getLogger(__name__)

service_api = Blueprint('service', __name__)


@service_api.route("/db-health")
def database_health_check():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok'})
    except OperationalError as ex:
        logger.exception(f'Connection to database is not working.')
        return jsonify({'status': 'error', 'exception': ex.args[0]}), 503


@service_api.route("/version")
def version_route():
    return jsonify({'version': get_version()})


def get_version() -> str:
    """
    Retrieves version from the flask app.
    """
    if 'version' not in g:  # TODO tohle nefunguje https://trello.com/c/uW9HT1sx/111-v-getversion-verze-nikdy-neni-v-g
        g.version = read_version('development')

    return g.version


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
        return redirect(url_for("functional.home"))

    if request.method == "GET":
        return render_template('login.html')

    logger.info(request)
    user = get_app_user_by_email(request.form["username"])
    if user is None:
        logger.warn(f"User {request.form['username']} not found.")
        return redirect(url_for("service.login"))

    if not bcrypt.checkpw(request.form["password"].encode("utf-8"), user.pass_hash.encode("utf-8")):
        logger.warn(f"Invalid password for user {request.form['username']}.")
        return redirect(url_for("service.login"))

    user.set_authenticated(True)
    login_user(user)
    logger.info(f"User {request.form['username']} logged in.")
    flash('Logged in successfully.')
    return redirect(url_for("functional.home"))


@service_api.route('/logout')
@login_required
def logout():
    username = current_user.email
    logout_user()
    flash('Logged out successfully.')
    logger.info(f"User {username} logged out.")
    return redirect(url_for("functional.home"))
