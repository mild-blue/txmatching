import flask_restx


class Namespace(flask_restx.Namespace):

    @staticmethod
    def _combine_decorators(decorators):
        def resulting_decorator(func):
            for decorator in reversed(decorators):
                func = decorator(func)
            return func
        return resulting_decorator

    def request_body(self, model, security='bearer'):
        return self._combine_decorators([
            self.doc(security=security),
            self.expect(model, validate=True)
        ])

    def response_ok(self, model=None, description=None, code=200):
        return self.response(code, model=model, description=description)
        # TODOO: marshall instead (problem with enums, probably implement custom field.output) for enum fields
        # return self.marshal_with(model, code=code, description=description, mask=False, skip_none=True)

    def response_errors(self, model):
        return Namespace._combine_decorators([
            self.response(code=400, model=model, description='Wrong data format.'),
            self.response(code=401, model=model, description='Authentication failed.'),
            self.response(
                code=403,
                model=model,
                description='Access denied. You do not have rights to access this endpoint.'
            ),
            self.response(code=500, model=model, description='Unexpected error, see contents for details.')
        ])
