from txmatching.web.web_utils.namespace import Namespace

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

OPTIMIZER_NAMESPACE = 'optimizer'
optimizer_api = Namespace(OPTIMIZER_NAMESPACE)

REPORTS_NAMESPACE = 'reports'
report_api = Namespace(REPORTS_NAMESPACE)

ENUMS_NAMESPACE = 'enums'
enums_api = Namespace(ENUMS_NAMESPACE)

CROSSMATCH_NAMESPACE = 'crossmatch'
crossmatch_api = Namespace(CROSSMATCH_NAMESPACE)

# Note: namespace prefix urls are defined in txmatching.web.add_all_namespaces
