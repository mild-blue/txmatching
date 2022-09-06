from txmatching.web.error_handler import NamespaceWithErrorResponses
from txmatching.auth.user.user_auth_check import require_user_login


class Namespace(NamespaceWithErrorResponses):
    
    @staticmethod
    def _combine_decorators(decorators):
        def resulting_decorator(func):
            for decorator in reversed(decorators):
                func = decorator(func)
            return func

        return resulting_decorator

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

    def response_errors(self):
        return Namespace._combine_decorators([
            self.response_error_wrong_data(),
            self.response_error_unauthorized(),
            self.response_error_forbidden(),
            self.response_error_unexpected()
        ])
