import json
from collections import OrderedDict

import yaml
from flask import Flask
from flask_restx import Api
from openapi_spec_validator import validate_v2_spec

from txmatching.web import (PATH_TO_PUBLIC_SWAGGER_JSON, PATH_TO_SWAGGER_JSON,
                            PATH_TO_SWAGGER_YAML, add_all_namespaces,
                            add_external_namespaces, register_error_handlers)


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


class PublicSwaggerGenApp:
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
        add_external_namespaces(self.api)
        register_error_handlers(self.api)


def generate_private():
    with open(PATH_TO_SWAGGER_JSON, 'w') as f:
        swagger = SwaggerGenApp().api.__schema__
        swagger_without_ordered_dict = {k: dict(v) if isinstance(v, OrderedDict) else v for k, v in swagger.items()}
        json.dump(swagger_without_ordered_dict, f, ensure_ascii=False, indent=4)
    with open(PATH_TO_SWAGGER_YAML, 'w') as f:
        yaml.dump(swagger_without_ordered_dict, f, indent=4)
    return swagger_without_ordered_dict


def generate_public():
    with open(PATH_TO_PUBLIC_SWAGGER_JSON, 'w') as f:
        swagger = PublicSwaggerGenApp().api.__schema__
        swagger_without_ordered_dict = {k: dict(v) if isinstance(v, OrderedDict) else v for k, v in
                                        swagger.items()}
        json.dump(swagger_without_ordered_dict, f, ensure_ascii=False, indent=4)
    return swagger_without_ordered_dict


if __name__ == '__main__':
    private_swagger = generate_private()
    public_swagger = generate_public()
    validate_v2_spec(private_swagger)
    validate_v2_spec(public_swagger)
