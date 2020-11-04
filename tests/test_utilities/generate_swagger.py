from collections import OrderedDict

import yaml
from flask import Flask
from flask_restx import Api
from openapi_spec_validator import validate_v2_spec

from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import add_all_namespaces, register_error_handlers

PATH_TO_SWAGGER_YAML = get_absolute_path('txmatching/web/swagger.yaml')


class SwaggerGenApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.app.config['SERVER_NAME'] = 'test'
        self.app.config['POSTGRES_USER'] = 'str'
        self.app.config['POSTGRES_PASSWORD'] = 'str'
        self.app.config['POSTGRES_DB'] = 'str'
        self.app.config['POSTGRES_URL'] = 'str'
        self.app.config['JWT_SECRET'] = 'str'
        self.app.config['JWT_EXPIRATION_DAYS'] = 10
        self.app.app_context().push()
        add_all_namespaces(self.api)
        register_error_handlers(self.api)


if __name__ == '__main__':
    app_for_swagger_gen = SwaggerGenApp()
    with open(PATH_TO_SWAGGER_YAML, 'w') as f:
        swagger = app_for_swagger_gen.api.__schema__
        swagger_without_ordered_dict = {k: dict(v) if isinstance(v, OrderedDict) else v for k, v in swagger.items()}
        yaml.dump(swagger_without_ordered_dict, f, indent=4)
    validate_v2_spec(swagger)
