from local_testing_utilities.populate_db import populate_large_db
from txmatching.web import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        populate_large_db()
