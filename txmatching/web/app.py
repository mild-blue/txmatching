import logging

from txmatching.database.migrate_db import migrate_db
from txmatching.web import create_app

app = create_app()
logger = logging.getLogger(__name__)

migrate_db(app.config['SQLALCHEMY_DATABASE_URI'])

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
