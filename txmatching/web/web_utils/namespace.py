import flask_restx
from flask_restx import fields

from txmatching.auth.user.user_auth_check import require_user_login


class Namespace(flask_restx.Namespace):

    @staticmethod
    def _combine_decorators(decorators):
        def resulting_decorator(func):
            for decorator in reversed(decorators):
                func = decorator(func)
            return func

        return resulting_decorator

    def _create_fail_response_model(self):
        return self.model('FailResponse', {
            'error': fields.String(required=True),
            'message': fields.String(required=False),
        })

    def require_user_login(self):
        return self._combine_decorators([
            self.doc(security='bearer'),
            require_user_login()
        ])

    def request_body(self, model, description: str = ''):
        return self._combine_decorators([
            self.doc(description=description),
            self.expect(model, validate=True)
        ])

    def response_ok(self, model=None, description=None, code=200):
        return self.response(code, model=model, description=description)
        # TODOO: marshall instead (problem with enums, probably implement custom field.output) for enum fields
        # return self.marshal_with(model, code=code, description=description, mask=False, skip_none=True)

    def response_error_matching_not_found(self):
        model = self._create_fail_response_model()
        return self.response(code=404, model=model, description='Matching for provided id was not found.')

    def response_error_non_unique_patients_provided(self):
        model = self._create_fail_response_model()
        return self.response(code=409, model=model, description='Non-unique patients provided.')

    def response_error_unexpected(self):
        model = self._create_fail_response_model()
        return self.response(code=500, model=model, description='Unexpected error, see contents for details.')

    def response_error_services_failing(self):
        model = self._create_fail_response_model()
        return self.response(code=503, model=model, description='Some services are failing.')

    def response_error_sms_gate(self):
        model = self._create_fail_response_model()
        return self.response(code=503, model=model, description='It was not possible to reach the SMS gate, '
                                                                'thus the one time password could not be send.')

    def response_errors(self):
        model = self._create_fail_response_model()
        return Namespace._combine_decorators([
            self.response(code=400, model=model, description='Wrong data format.'),
            self.response(code=401, model=model, description='Authentication failed.'),
            self.response(code=403, model=model,
                          description='Access denied. You do not have rights to access this endpoint.'),
            self.response_error_unexpected()
        ])
