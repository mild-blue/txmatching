import logging
import os
import sys
import traceback

from flask import Flask, render_template, request

from kidney_exchange.database.db import db
from kidney_exchange.web.version_api import version_api


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# register blueprints
app.register_blueprint(version_api)


def configure_db():
    # TODO load configuration from file and override it with env - to discussion with team
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    url = os.environ.get("POSTGRES_URL")
    po_db = os.environ.get("POSTGRES_DB")

    app.config['SQLALCHEMY_DATABASE_URI'] \
        = f'postgresql+psycopg2://{user}:{password}@{url}/{po_db}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


with app.app_context():
    configure_db()


@app.route('/')
def hello():
    logger.info("Hello from the log!")
    return "Hello World!"


if __name__ == '__main__':
    app.run(port=8080)
