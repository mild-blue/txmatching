from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.web.api.namespaces import patient_api

HLA_ANTIBODY = patient_api.model('HlaAntibody', {
    'name': fields.String(required=True),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.String(required=True)
})

HLA_TYPING = patient_api.model('HlaTyping', {
    'codes': fields.List(required=True, cls_or_instance=fields.String),
})

HLA_ANTIBODIES = patient_api.model('HlaAntibodies', {
    'hla_antibodies': fields.List(required=True, cls_or_instance=fields.Nested(HLA_ANTIBODY)),
    'antibodies_over_cutoff': fields.List(required=True, cls_or_instance=fields.String),
})

PATIENT_PARAMETERS_MODEL = patient_api.model('PatientParameters', {
    'blood_group': fields.String(required=False),
    'hla_typing': fields.List(required=False, cls_or_instance=fields.String),
    'country_code': fields.String(required=False)
})

RECIPIENT_REQUIREMENTS = patient_api.model('RecipientRequirements', {
    'require_better_match_in_compatibility_index': fields.Boolean(required=True),
    'require_better_match_in_compatibility_index_or_blood_group': fields.Boolean(required=True),
    'require_compatible_blood_group': fields.Boolean(required=True)
})

DONOR_MODEL = patient_api.model('Donor', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PATIENT_PARAMETERS_MODEL),
    'donor_type': fields.String(required=True, enum=[donor_type.name for donor_type in DonorType]),
    'related_recipient_db_id': fields.Integer(required=False, description='Database id of the related recipient'),
})

RECIPIENT_MODEL = patient_api.model('Recipient', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PATIENT_PARAMETERS_MODEL),
    'hla_antibodies': fields.Nested(required=True, model=HLA_ANTIBODIES),
    'related_donor_db_id': fields.Integer(required=True, description='Database id of the related donor'),
    'recipient_requirements': fields.Nested(RECIPIENT_REQUIREMENTS)
})

PATIENTS_MODEL = patient_api.model('Patients', {
    'recipients': fields.List(required=False, cls_or_instance=fields.Nested(RECIPIENT_MODEL)),
    'donors': fields.List(required=False, cls_or_instance=fields.Nested(DONOR_MODEL))
})
