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

TXM_EVENT_NAMESPACE = 'txm-event'
txm_event_api = Namespace(TXM_EVENT_NAMESPACE)

REPORTS_NAMESPACE = 'reports'
report_api = Namespace(REPORTS_NAMESPACE)

ENUMS_NAMESPACE = 'enums'
enums_api = Namespace(ENUMS_NAMESPACE)

# Note: namespace prefix urls are defined in txmatching.web.add_all_namespaces
