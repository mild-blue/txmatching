from local_testing_utilities.populate_db import populate_db_multiple_recipients
from txmatching.web import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        populate_db_multiple_recipients()
