# -*- coding: utf-8 -*-
#  based on https://pypi.org/project/swagger-tester/ just raw code to test swagger somehow, some alterations were
# made to make it work in our project. The project is under MIT license
# pylint: skip-file
# skipping as this is just code for testing
import json
import logging
import time
from typing import Dict, Set
from urllib.parse import urlencode

import six
from flask.testing import FlaskClient

from tests.test_utilities.swagger_testing.swagger_parser import SwaggerParser

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# The swagger path item object (as well as HTTP) allows for the following
# HTTP methods (http://swagger.io/specification/#pathItemObject):
_HTTP_METHODS = ['put', 'post', 'get', 'delete', 'options', 'head', 'patch']


def get_request_args(path, action, swagger_parser):
    """Get request args from an action and a path.

    Args:
        path: path of the action.
        action: action of the request(get, delete, post, put).
        swagger_parser: instance of SwaggerParser.

    Returns:
        A dict of args to transmit to bravado.
    """
    request_args = {}
    if path in swagger_parser.paths.keys() and action in swagger_parser.paths[path].keys():
        operation_spec = swagger_parser.paths[path][action]

        if 'parameters' in operation_spec.keys():
            for param_name, param_spec in operation_spec['parameters'].items():
                request_args[param_name] = swagger_parser.get_example_from_prop_spec(param_spec)

    return request_args


def validate_definition(swagger_parser, valid_response, response):
    """Validate the definition of the response given the given specification and body.

    Args:
        swagger_parser: instance of swagger parser.
        valid_response: valid response answer from spec.
        response: response of the request.
    """
    # additionalProperties do not match any definition because the keys
    # vary. we can only check the type of the values
    if 'any_prop1' in valid_response and 'any_prop2' in valid_response:
        assert swagger_parser.validate_additional_properties(valid_response, response)
        return

    # No answer
    if response is None or response == '':
        assert valid_response == '' or valid_response is None
        return

    if valid_response == '' or valid_response is None:
        assert response is None or response == ''
        return

    # Validate output definition
    if isinstance(valid_response, list):  # Return type is a list
        assert isinstance(response, list)
        if response:
            valid_response = valid_response[0]
            response = response[0]
        else:
            return

    # Not a dict and not a text
    if ((not isinstance(response, dict) or not isinstance(valid_response, dict)) and
            (not isinstance(response, (six.text_type, six.string_types)) or
             not isinstance(valid_response, (six.text_type, six.string_types)))):
        assert type(response) == type(valid_response)
    elif isinstance(response, dict) and isinstance(valid_response, dict):
        # Check if there is a definition that match body and response
        valid_definition = swagger_parser.get_dict_definition(valid_response, get_list=True)
        actual_definition = swagger_parser.get_dict_definition(response, get_list=True)
        assert len(set(valid_definition).intersection(actual_definition)) >= 1, \
            f'Responses {valid_response} and {response} not compatible'


def parse_parameters(url, action, path, request_args, swagger_parser):
    """Parse the swagger parameters to make a request.

    Replace var in url, make query dict, body and headers.

    Args:
        url: url of the request.
        action: HTTP action.
        path: path of the request.
        request_args: dict of args to send to the request.
        swagger_parser: instance of swagger parser.

    Returns:
        (url, body, query_params, headers, files)
    """
    body = None
    query_params = {}
    files = {}
    headers = [('Content-Type', 'application/json')]

    if path in swagger_parser.paths.keys() and action in swagger_parser.paths[path].keys():
        operation_spec = swagger_parser.paths[path][action]

        # Get body and path
        for parameter_name, parameter_spec in operation_spec['parameters'].items():
            if parameter_spec['in'] == 'body':
                body = request_args[parameter_name]
            elif parameter_spec['in'] == 'path':
                url = url.replace('{{{0}}}'.format(parameter_name), str(request_args[parameter_name]))
            elif parameter_spec['in'] == 'query':
                if isinstance(request_args[parameter_name], list):
                    query_params[parameter_name] = ','.join(request_args[parameter_name])
                else:
                    query_params[parameter_name] = str(request_args[parameter_name])
            elif parameter_spec['in'] == 'formData':
                if body is None:
                    body = {}

                if (isinstance(request_args[parameter_name], tuple) and
                        hasattr(request_args[parameter_name][0], 'read')):
                    files[parameter_name] = (request_args[parameter_name][1],
                                             request_args[parameter_name][0])
                else:
                    body[parameter_name] = request_args[parameter_name]

                # The first header is always content type, so just replace it so we don't squash custom headers
                headers[0] = ('Content-Type', 'multipart/form-data')
            elif parameter_spec['in'] == 'header':
                header_value = request_args.get(parameter_name)
                header_value = header_value or parameter_spec.get('default', '')
                headers += [(parameter_spec['name'], str(header_value))]
    return url, body, query_params, headers, files


def get_url_body_from_request(action, path, request_args, swagger_parser):
    """Get the url and the body from an action, path, and request args.

    Args:
        action: HTTP action.
        path: path of the request.
        request_args: dict of args to send to the request.
        swagger_parser: instance of swagger parser.

    Returns:
        url, body, headers, files
    """
    url, body, query_params, headers, files = parse_parameters(path, action, path, request_args, swagger_parser)

    url = '{0}?{1}'.format(url, urlencode(query_params))

    if ('Content-Type', 'multipart/form-data') not in headers:
        try:
            if body:
                body = json.dumps(body)
        except TypeError as exc:
            logger.warning(u'Cannot decode body: {0}.'.format(repr(exc)))
    else:
        headers.remove(('Content-Type', 'multipart/form-data'))

    return url, body, headers, files


def get_method_from_action(client, action):
    """Get a client method from an action.

    Args:
        client: flask client.
        action: action name.

    Returns:
        A flask client function.
    """
    error_msg = "Action '{0}' is not recognized; needs to be one of {1}.".format(action, str(_HTTP_METHODS))
    assert action in _HTTP_METHODS, error_msg

    return client.__getattribute__(action)


def swagger_test(swagger_yaml_path: str,
                 expected_status_codes: Set[int],
                 app_client: FlaskClient,
                 special_status_code_for_paths=None,
                 wait_time_between_tests: int = 0,
                 use_example: bool = True,
                 extra_headers: Dict[str, str] = None):
    """Test the given swagger api.

    Test with either a swagger.yaml path for with an API
    URL if you have a running API.

    Args:
        swagger_yaml_path: path of your YAML swagger file.
        app_client: Client of the swagger api.
        expected_status_codes: Expected status codes
        special_status_code_for_paths: dict containing the error you don't want to raise.
                         ex: {
                            'get': {
                                '/pet/': ['404']
                            }
                         }
                         Will ignore 404 when getting a pet.
        wait_time_between_tests: an number that will be used as waiting time between tests [in seconds].
        use_example: use example of your swagger file instead of generated data.
        extra_headers: additional headers you may want to send for all operations

    Raises:
        ValueError: In case you specify neither a swagger.yaml path or an app URL.
    """

    if special_status_code_for_paths is None:
        special_status_code_for_paths = {}
    if extra_headers is None:
        extra_headers = {}
    for _ in swagger_test_yield(swagger_yaml_path=swagger_yaml_path,
                                app_client=app_client,
                                expected_status_codes=expected_status_codes,
                                special_status_code_for_paths=special_status_code_for_paths,
                                wait_time_between_tests=wait_time_between_tests,
                                use_example=use_example,
                                extra_headers=extra_headers):
        pass


def swagger_test_yield(swagger_yaml_path: str,
                       expected_status_codes: Set[int],
                       app_client: FlaskClient,
                       special_status_code_for_paths: Dict[str, Dict[str, int]],
                       wait_time_between_tests: int,
                       use_example: bool,
                       extra_headers: Dict[str, str]):
    """Test the given swagger api. Yield the action and operation done for each test.

    Test with either a swagger.yaml path with an API
    URL if you have a running API.

    Returns:
        Yield between each test: (action, operation)

    Raises:
        ValueError: In case you specify neither a swagger.yaml path or an app URL.
    """
    if extra_headers is None:
        extra_headers = {}
    if special_status_code_for_paths is None:
        special_status_code_for_paths = {}

    swagger_parser = SwaggerParser(swagger_yaml_path, use_example=use_example)

    print(f'Starting testrun against {swagger_yaml_path} or {app_client} using examples: {use_example}')

    operation_sorted = {method: [] for method in _HTTP_METHODS}

    # Sort operation by action
    operations = swagger_parser.operation.copy()
    operations.update(swagger_parser.generated_operation)
    for operation, request in operations.items():
        operation_sorted[request[1]].append((operation, request))

    postponed = []

    # For every operationId
    for action in _HTTP_METHODS:
        for operation in operation_sorted[action]:
            # Make request
            path = operation[1][0]
            action = operation[1][1]
            client_name = getattr(app_client, '__name__', 'FlaskClient')

            request_args = get_request_args(path, action, swagger_parser)
            logger.info(f'Sending {request_args} to {path} via {action}')
            url, body, headers, files = get_url_body_from_request(action, path, request_args, swagger_parser)

            logger.info(u'TESTING {0} {1}'.format(action.upper(), url))

            # Add any extra headers specified by the user
            headers.extend([(key, value) for key, value in extra_headers.items()])

            response = get_method_from_action(app_client, action)(url,
                                                                  headers=dict(headers),
                                                                  data=body)

            logger.info(u'Using {0}, got status code {1} for ********** {2} {3}'.format(
                client_name, response.status_code, action.upper(), url))

            # Check if authorize error
            if action in special_status_code_for_paths and path in special_status_code_for_paths[action]:
                if response.status_code in special_status_code_for_paths[action][path]:
                    logger.info(f'Got expected authorized error on {url} with status {response.status_code}')
                else:
                    raise AssertionError(f'Invalid status code for path {path}, action {action} and body: {body}: '
                                         f'{response.status_code}')
            elif response.status_code not in expected_status_codes:
                raise AssertionError(f'Status code {response.status_code} was not expected '
                                     f'for path {path}, action {action} and body: {body}: ')

            if response.status_code != 404:
                # Get valid request and response body
                body_req = swagger_parser.get_send_request_correct_body(path, action)

                try:
                    response_spec = swagger_parser.get_request_data(path, action, body_req)
                except (TypeError, ValueError) as exc:
                    logger.warning(u'Error in the swagger file: {0}'.format(repr(exc)))
                    continue

                # Get response data
                response_json = response.json

                if response.status_code in response_spec.keys():
                    validate_definition(swagger_parser, response_spec[response.status_code], response_json)
                # elif 'default' in response_spec.keys():
                #     validate_definition(swagger_parser, response_spec['default'], response_json)
                else:
                    raise AssertionError(f'Invalid status code for path {path}, action {action} and body: {body}: '
                                         f'{response.status_code}.'
                                         f' Expected: {response_spec.keys()}')

                if wait_time_between_tests > 0:
                    time.sleep(wait_time_between_tests)

                yield (action, operation)
            else:
                # 404 => Postpone retry
                if {'action': action, 'operation': operation} in postponed:  # Already postponed => raise error
                    raise Exception(u'Invalid status code {0}'.format(response.status_code))

                operation_sorted[action].append(operation)
                postponed.append({'action': action, 'operation': operation})
                yield (action, operation)
                continue
