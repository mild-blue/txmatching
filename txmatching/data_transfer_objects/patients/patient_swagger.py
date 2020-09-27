from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Sex
from txmatching.web.api.namespaces import patient_api

BLOOD_TYPES = ['A', 'B', 'AB', '0']

HLA_ANTIBODY = patient_api.model('HlaAntibody', {
    'raw_code': fields.String(required=True),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.String(required=True),
    'code': fields.String(required=False)
})

HLA_TYPE = patient_api.model('HlaType', {
    'code': fields.List(required=True, cls_or_instance=fields.String),
    'raw_code': fields.String(required=True),
})

HLA_TYPING = patient_api.model('HlaTyping', {
    'hla_types_list': fields.List(required=True, cls_or_instance=fields.Nested(HLA_TYPE)),
    'codes': fields.List(required=True, cls_or_instance=fields.String),
})

HLA_ANTIBODIES = patient_api.model('HlaAntibodies', {
    'hla_antibodies_list': fields.List(required=True, cls_or_instance=fields.Nested(HLA_ANTIBODY)),
    'hla_codes_over_cutoff': fields.List(required=True, cls_or_instance=fields.String),
})

PATIENT_PARAMETERS_MODEL = patient_api.model('PatientParameters', {
    'blood_group': fields.String(required=False, enum=BLOOD_TYPES),
    'hla_typing': fields.List(required=False, cls_or_instance=fields.Nested(HLA_TYPING)),
    'country_code': fields.String(required=False),
    'sex': fields.String(required=False, enum=[sex.name for sex in Sex]),
    'height': fields.Integer(required=False),
    'weight': fields.Float(required=False),
    'YOB': fields.Integer(required=False),
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
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_TYPES)),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PATIENT_PARAMETERS_MODEL),
    'hla_antibodies': fields.Nested(required=True, model=HLA_ANTIBODIES),
    'related_donor_db_id': fields.Integer(required=True, description='Database id of the related donor'),
    'recipient_requirements': fields.Nested(RECIPIENT_REQUIREMENTS),
    'waiting_since': fields.DateTime(required=False),
    'previous_transplants': fields.Integer(required=False),
})

PATIENTS_MODEL = patient_api.model('Patients', {
    'recipients': fields.List(required=False, cls_or_instance=fields.Nested(RECIPIENT_MODEL)),
    'donors': fields.List(required=False, cls_or_instance=fields.Nested(DONOR_MODEL))
})

HLA_ANTIBODY_TO_UPDATE = patient_api.model('HlaAntibodyToUpdate', {
    'raw_code': fields.String(required=True),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.Integer(required=True),
})

HLA_TYPE_TO_UPDATE = patient_api.model('HlaTypeToUpdate', {
    'raw_code': fields.String(required=True),
})

HLA_TYPING_TO_UPDATE = patient_api.model('HlaTyping', {
    'hla_types_list': fields.List(required=True, cls_or_instance=fields.Nested(HLA_TYPE_TO_UPDATE)),
})

HLA_ANTIBODIES_TO_UPDATE = patient_api.model('HlaAntibodies', {
    'hla_antibodies_list': fields.List(required=True, cls_or_instance=fields.Nested(HLA_ANTIBODY_TO_UPDATE)),
})

RECIPIENT_MODEL_TO_UPDATE = patient_api.model('RecipientModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_TYPES)),
    'hla_typing': fields.Nested(HLA_TYPING_TO_UPDATE),
    'hla_antibodies': fields.Nested(HLA_ANTIBODIES_TO_UPDATE),
    'recipient_requirements': fields.Nested(RECIPIENT_REQUIREMENTS)
})

DONOR_MODEL_TO_UPDATE = patient_api.model('DonorModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'hla_typing': fields.Nested(HLA_TYPING_TO_UPDATE),
})
