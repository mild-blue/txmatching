from flask_restx import Namespace

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

REPORTS_NAMESPACE = 'reports'
report_api = Namespace(REPORTS_NAMESPACE)

DUMMY_MATCHING_NAMESPACE = 'dummy-matching'
dummy_matching_api = Namespace(DUMMY_MATCHING_NAMESPACE)
