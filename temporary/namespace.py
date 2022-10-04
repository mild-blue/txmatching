import flask_restx

class Namespace(flask_restx.Namespace):

    @staticmethod
    def _combine_decorators(decorators):
        def resulting_decorator(func):
            for decorator in reversed(decorators):
                func = decorator(func)
            return func

        return resulting_decorator

    def request_body(self, model, description: str = ''):
        return self._combine_decorators([
            self.doc(description=description),
            self.expect(model, validate=False)
        ])

    def response_ok(self, model=None, description=None, code=200):
        return self.response(code, model=model, description=description)
