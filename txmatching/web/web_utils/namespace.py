from typing import Dict, List, Set, Tuple

import flask_restx

from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.web.error_handler import generate_namespace_error_info


class Namespace(flask_restx.Namespace):

    __ERROR_INFO: Dict[type, Tuple[str, int]] = generate_namespace_error_info()

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

    def response_errors(self, exceptions: Set[type]):
        """
        Creating response decorators for given exceptions.
        :param exceptions: list of exceptions for creating responses from error_handler.py
        :return: combined decorators for error responses.
        """
        fail_model = self._create_fail_response_model()
        exceptions = Namespace._sort_exceptions_by_code(exceptions)

        response_decorators = []
        for ex_idx, exception in enumerate(exceptions):
            # TODO: delete assert if _sort enabled (https://github.com/mild-blue/txmatching/pull/982#discussion_r974438100
            assert exception in Namespace.__ERROR_INFO, f'There is no definitive response for ' \
                                                        f'{exception.__name__} in error-handler.'

            combined_description = Namespace._create_combined_description_for_duplicates(exceptions,
                                                                                         ex_idx)
            description = combined_description if combined_description else \
                Namespace.__ERROR_INFO[exception].description

            response_decorators.append(self.response(code=Namespace.__ERROR_INFO[exception].code,
                                                     description=description,
                                                     model=fail_model))

        return self._combine_decorators(response_decorators)

    @classmethod
    def _create_combined_description_for_duplicates(cls, exceptions: Set[type], exception_idx: int) -> str:
        """
        Creates combined descriptions for error responses with the same code.
        Info about exception is taken from cls.__ERROR_INFO
        :param exceptions: list of exceptions, where to search duplicates
        :param exception_idx: exception's idx. Searching duplicates starting from it.
        :return: combined description for all duplicates. If no duplicates, returns ''.
        """
        # searching duplicates for exception in exceptions
        exceptions = list(exceptions)
        exception = exceptions[exception_idx]
        duplicates = [error for error, info in cls.__ERROR_INFO.items() if
                      error in exceptions and
                      cls.__ERROR_INFO[exception].code == info.code]
        # creating combined_description
        if len(duplicates) > 1:
            # creating combined_description
            descriptions = [cls.__ERROR_INFO[error].description for error in duplicates]
            combined_description = '/'.join(descriptions)

            return combined_description

        return ''

    @classmethod
    def _sort_exceptions_by_code(cls, exceptions: Set[type]):
        """
        Sorting list of exceptions by code.
        Info about exceptions is taken from cls.__ERROR_INFO.
        :return: sorted list.
        """
        def key_func(exception):
            assert exception in cls.__ERROR_INFO, f'There is no definitive response ' \
                                                  f'for {exception.__name__} in error-handler.'
            return cls.__ERROR_INFO[exception].code

        return sorted(exceptions, key=key_func)
