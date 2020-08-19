from flask_restx import Namespace

PATIENT_NAMESPACE = 'patients'
patient_api = Namespace(PATIENT_NAMESPACE)

MATCHING_NAMESPACE = 'matching'
matching_api = Namespace(MATCHING_NAMESPACE)
