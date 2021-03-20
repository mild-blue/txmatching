from http import HTTPStatus

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
        return self.doc(body=model, security=security)

    def response_success(self, model, description=None, code=200):
        return self.response(code, model=model, description=description)
        # TODOO: marshall instead
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


def response_ok(data):
    return data


PATIENT_NAMESPACE = 'patients'
patient_api = Namespace(PATIENT_NAMESPACE)

MATCHING_NAMESPACE = 'matching'
matching_api = Namespace(MATCHING_NAMESPACE)

SERVICE_NAMESPACE = 'service'
service_api = Namespace(SERVICE_NAMESPACE)

USER_NAMESPACE = 'user'
user_api = Namespace(USER_NAMESPACE)

CONFIGURATION_NAMESPACE = 'configuration'
configuration_api = Namespace(CONFIGURATION_NAMESPACE)

TXM_EVENT_NAMESPACE = 'txm-event'
txm_event_api = Namespace(TXM_EVENT_NAMESPACE)

PUBLIC_NAMESPACE = 'public'
public_api = Namespace(PUBLIC_NAMESPACE)


REPORTS_NAMESPACE = 'reports'
report_api = Namespace(REPORTS_NAMESPACE)

ENUMS_NAMESPACE = 'enums'
enums_api = Namespace(ENUMS_NAMESPACE)

# Note: namespace prefix urls are defined in txmatching.web.add_all_namespaces
