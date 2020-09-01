from flask_restx import fields

from txmatching.patients.patient import PatientType
from txmatching.web.api.namespaces import patient_api

PATIENT_PARAMETERS_MODEL = patient_api.model('Patient Parameters', {
    "blood_group": fields.String(required=False),
    "acceptable_blood_groups": fields.List(required=False, cls_or_instance=fields.String),
    "hla_antigens": fields.List(required=False, cls_or_instance=fields.String),
    "hla_antibodies": fields.List(required=False, cls_or_instance=fields.String),
    "country_code": fields.String(required=False),

})

PATIENT_MODEL = patient_api.model('Patient', {
    "db_id": fields.Integer(required=True, description='Database id of the patient'),
    "medical_id": fields.String(required=True, description='Medical id of the patient'),
    "parameters": fields.Nested(required=True, model=PATIENT_PARAMETERS_MODEL),
    "patient_type": fields.String(required=True, enum=[v.name for v in PatientType])
})
