import json
from collections import OrderedDict

import yaml
from flask import Flask
from flask_restx import Api
from openapi_spec_validator import validate_v2_spec

from txmatching.web import (AUTHORIZATIONS, PATH_TO_PUBLIC_SWAGGER_JSON,
                            PATH_TO_SWAGGER_JSON, PATH_TO_SWAGGER_YAML,
                            add_all_namespaces, add_public_namespaces,
                            register_error_handlers)

_PATH_ARGS_ORDER = {
    'parameters': 1,
    'get': 2,
    'post': 3,
    'put': 4,
    'delete': 5,
}


# pylint: disable=too-few-public-methods
# these classes are useful as wrappers to run the generators
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
        self.app.config['ENVIRONMENT'] = 'PRODUCTION'
        self.app.config['COLOUR_SCHEME'] = 'IKEM'
        self.app.config['USE_2FA'] = 'FALSE'
        self.app.config['AUTHENTIC_CLIENT_ID'] = 'f5c6b6a72ff4f7bbdde383a26bdac192b2200707'
        self.app.config['AUTHENTIC_CLIENT_SECRET'] = '37e841e70b842a0d1237b3f7753b5d7461307562568b5add7edcfa66' \
                                                     '30d578fdffb7ff4d5c0f845d10f8f82bc1d80cec62cb397fd48795a5b1b' \
                                                     'ee6090e0fa409'
        self.app.config['AUTHENTIC_REDIRECT_URI'] = 'http://localhost:8080/v1/user/authentik-login'
        self.api.authorizations = AUTHORIZATIONS
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
        self.app.config['ENVIRONMENT'] = 'PRODUCTION'
        self.app.config['COLOUR_SCHEME'] = 'IKEM'
        self.app.config['USE_2FA'] = 'FALSE'
        self.app.config['AUTHENTIC_CLIENT_ID'] = 'f5c6b6a72ff4f7bbdde383a26bdac192b2200707'
        self.app.config['AUTHENTIC_CLIENT_SECRET'] = '37e841e70b842a0d1237b3f7753b5d7461307562568b5add7edcfa66' \
                                                     '30d578fdffb7ff4d5c0f845d10f8f82bc1d80cec62cb397fd48795a5b1b' \
                                                     'ee6090e0fa409'
        self.app.config['AUTHENTIC_REDIRECT_URI'] = 'http://localhost:8080/v1/user/authentik-login'
        self.api.authorizations = AUTHORIZATIONS
        self.app.app_context().push()
        add_public_namespaces(self.api)
        register_error_handlers(self.api)


def _api_to_swagger(api: Api) -> dict:
    swagger = api.__schema__
    del swagger['host']
    del swagger['responses']

    # Sort attributes so that the output would be deterministic
    swagger['paths'] = {
        path: OrderedDict(
            sorted(
                props_dict.items(),
                key=lambda kv: (_PATH_ARGS_ORDER.get(kv[0], 100), kv[0])
            )
        )
        for path, props_dict in swagger['paths'].items()
    }
    swagger['definitions'] = OrderedDict(
        sorted(swagger['definitions'].items())
    )

    return swagger


def generate_private():
    with open(PATH_TO_SWAGGER_JSON, 'w', encoding='utf-8') as file:
        swagger = _api_to_swagger(SwaggerGenApp().api)
        json.dump(swagger, file, ensure_ascii=False, indent=4)

    yaml.Dumper.add_representer(
        OrderedDict,
        lambda dumper, data: dumper.represent_dict(data.items())
    )
    with open(PATH_TO_SWAGGER_YAML, 'w', encoding='utf-8') as file:
        yaml.dump(swagger, file, indent=4, Dumper=yaml.Dumper)
    return swagger


def generate_public():
    with open(PATH_TO_PUBLIC_SWAGGER_JSON, 'w', encoding='utf-8') as file:
        swagger = _api_to_swagger(PublicSwaggerGenApp().api)
        json.dump(swagger, file, ensure_ascii=False, indent=4)
    return swagger


if __name__ == '__main__':
    private_swagger = generate_private()
    public_swagger = generate_public()
    validate_v2_spec(private_swagger)
    validate_v2_spec(public_swagger)
