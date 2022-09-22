from typing import Dict, List, NamedTuple, Set

import flask_restx

from txmatching.auth.exceptions import (AuthenticationException,
                                        InvalidAuthCallException,
                                        InvalidOtpException)
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.web.error_handler import _user_auth_handlers


def _generate_namespace_error_info() -> Dict[type, NamedTuple]:
    """
    Activates decorator @_namespace_error_responses (error_handler.py) for
    generating error information dict by exception as a key.
    :return: dict of information about exceptions as a key.
    """
    fake_api = flask_restx.Api()
    _user_auth_handlers(fake_api)

    responses = {}
    ErrorInfo = NamedTuple('ErrorInfo', [('description', str), ('code', int)])
    for exception, handle_function in fake_api.error_handlers.items():
        if hasattr(handle_function, 'code') and hasattr(handle_function, 'description'):
            responses[exception] = ErrorInfo._make((handle_function.description,
                                                    handle_function.code))

    return responses


class Namespace(flask_restx.Namespace):

    __ERROR_INFO: Dict[type, NamedTuple] = _generate_namespace_error_info()
    __DEFAULT_ERRORS_FOR_RESPONSES = {KeyError,
                                      InvalidOtpException,
                                      AuthenticationException,
                                      InvalidAuthCallException}

    @staticmethod
    def _combine_decorators(decorators):
        def resulting_decorator(func):
            for decorator in reversed(decorators):
                func = decorator(func)
            return func

        return resulting_decorator

    def _create_fail_response_model(self):
        return self.model('FailResponse', {
            'error': flask_restx.fields.String(required=True),
            'message': flask_restx.fields.String(required=False),
        })

    def require_user_login(self):
        return self._combine_decorators([
            self.doc(security='bearer'),
            require_user_login()
        ])

    def request_body(self, model, description: str = ''):
        return self._combine_decorators([
            self.doc(description=description),
            self.expect(model, validate=False)
        ])

    def request_arg_int(
            self,
            param: str,
            description: str = '',
            required: bool = True,
    ):
        return self.doc(
            params={
                param: {
                    'description': f'{description} Example: {param}=42',
                    'type': int,
                    'required': required
                }
            }
        )

    def request_arg_bool(
            self,
            param: str,
            description: str = '',
            required: bool = True,
    ):
        return self.doc(
            params={
                param: {
                    'description': f'{description} Example: {param}=true, {param}=1, {param}=FaLse',
                    'type': bool,
                    'required': required
                }
            }
        )

    def request_arg_flag(
            self,
            param: str,
            description: str = ''
    ):
        return self.doc(
            params={
                param: {
                    'description': f'{description} Example: ?{param}',
                    'type': bool,
                    'required': False
                }
            }
        )

    def response_ok(self, model=None, description=None, code=200):
        return self.response(code, model=model, description=description)
        # TODO: marshall instead https://github.com/mild-blue/txmatching/issues/562
        # return self.marshal_with(model, code=code, description=description, mask=False, skip_none=True)

    def response_errors(self, exceptions: Set[type],
                        add_default_namespace_errors: bool = False,
                        duplicates_allowed: bool = False):
        """
        Creating response decorators for given exceptions.
        :param exceptions: list of exceptions for creating responses from error_handler.py
        :param add_default_namespace_errors: set True to add exceptions from __DEFAULT_ERRORS_FOR_RESPONSES
        :param duplicates_allowed: set True to allow creating many responses for this exception with the same status code
        :return: combined decorators for error responses.
        """
        if add_default_namespace_errors:
            # adding most common errors, which are used for apis
            # (edit them in Namespace.__DEFAULT_ERRORS_FOR_RESPONSES)
            exceptions = exceptions.union(Namespace.__DEFAULT_ERRORS_FOR_RESPONSES)

        fail_model = self._create_fail_response_model()
        exceptions: List[type] = Namespace._sort_exceptions_by_code(exceptions)  # + existence check

        response_decorators = []
        for ex_idx, exception in enumerate(exceptions):
            description = Namespace._create_combined_description_for_duplicates(exceptions,
                                                                                ex_idx,
                                                                                duplicates_allowed)
            response_decorators.append(self.response(code=Namespace.__ERROR_INFO[exception].code,
                                                     description=description,
                                                     model=fail_model))

        return self._combine_decorators(response_decorators)

    @classmethod
    def _create_combined_description_for_duplicates(cls, exceptions: List[type], exception_idx: int,
                                                    duplicates_allowed: bool) -> str:
        """
        Creates combined descriptions for error responses with the same code.
        Info about exception is taken from cls.__ERROR_INFO
        :param exceptions: list of exceptions, where to search duplicates
        :param exception_idx: exception's idx. Searching duplicates starting from it.
        :param duplicates_allowed: set True to allow creating many responses for this exception
                                     with the same status code
        :return: combined description for all duplicates. If duplicates are created without permission,
                                                            AssertionError would be raised.
        """
        # searching duplicates for exception in exceptions
        exception = exceptions[exception_idx]
        duplicates = [error for error, info in cls.__ERROR_INFO.items() if
                      error in exceptions and
                      cls.__ERROR_INFO[exception].code == info.code]
        if len(duplicates) > 1:
            assert duplicates_allowed, f'Several errors ({duplicates} have the same response code. ' \
                                       f'Set duplicates_allowed=True in response_errors decorator.'

        # creating combined_description
        descriptions = [cls.__ERROR_INFO[error].description for error in duplicates]
        combined_description = '/'.join(descriptions)

        return combined_description

    @classmethod
    def _sort_exceptions_by_code(cls, exceptions: Set[type]) -> List[type]:
        """
        Sorting set of exceptions by code.
        Info about exceptions is taken from cls.__ERROR_INFO.
        :return: sorted list of exceptions. AssertionError will be raised in case of
                                                  exception's non-existence in __ERROR_INFO.
        """
        def key_func(exception):
            assert exception in cls.__ERROR_INFO, f'There is no definitive response ' \
                                                  f'for {exception.__name__} in error-handler.'
            return cls.__ERROR_INFO[exception].code

        return sorted(exceptions, key=key_func)
