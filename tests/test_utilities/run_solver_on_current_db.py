from flask import g

from txmatching.config.configuration import Configuration
from txmatching.database.services.config_service import \
    save_configuration_as_current
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.web import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        g.user_id = 1
        configuration = Configuration(max_number_of_distinct_countries_in_round=0)
        save_configuration_as_current(configuration)
        res = solve_from_db()
        print(len(list(res)))
