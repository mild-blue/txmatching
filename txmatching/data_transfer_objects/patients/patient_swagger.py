from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.web.api.namespaces import patient_api

PATIENT_PARAMETERS_MODEL = patient_api.model('Patient Parameters', {
    "blood_group": fields.String(required=False),
    "hla_antigens": fields.List(required=False, cls_or_instance=fields.String),
    "hla_antibodies": fields.List(required=False, cls_or_instance=fields.String),
    "country_code": fields.String(required=False),

})

RECIPIENT_REQUIREMENTS = patient_api.model('Recipient Requirements', {
    "require_better_match_in_compatibility_index": fields.Boolean(required=True),
    "require_better_match_in_compatibility_index_or_blood_group": fields.Boolean(required=True),
    "require_compatible_blood_group": fields.Boolean(required=True)
})

DONOR_MODEL = patient_api.model('Donor', {
    "db_id": fields.Integer(required=True, description='Database id of the patient'),
    "medical_id": fields.String(required=True, description='Medical id of the patient'),
    "parameters": fields.Nested(required=True, model=PATIENT_PARAMETERS_MODEL),
    "donor_type": fields.String(required=True, enum=[v.name for v in DonorType]),
    "related_recipient_db_id": fields.Integer(required=False, description='Database id of the related recipient'),
})

RECIPIENT_MODEL = patient_api.model('Recipient', {
    "db_id": fields.Integer(required=True, description='Database id of the patient'),
    "acceptable_blood_groups": fields.List(required=False, cls_or_instance=fields.String),
    "medical_id": fields.String(required=True, description='Medical id of the patient'),
    "parameters": fields.Nested(required=True, model=PATIENT_PARAMETERS_MODEL),
    "related_donor_db_id": fields.Integer(required=False, description='Database id of the related donor'),
    "recipient_requiremens": fields.Nested(RECIPIENT_REQUIREMENTS)
})

PATIENTS_MODEL = patient_api.model('Patients', {
    "recipients": fields.List(required=False, cls_or_instance=fields.Nested(RECIPIENT_MODEL)),
    "donors": fields.List(required=False, cls_or_instance=fields.Nested(DONOR_MODEL))
})
