from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Sex
from txmatching.web.api.namespaces import patient_api

BLOOD_TYPES = ['A', 'B', 'AB', '0']

HLAAntibody = patient_api.model('HlaAntibody', {
    'raw_code': fields.String(required=True),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.String(required=True),
    'code': fields.String(required=False)
})

HLAType = patient_api.model('HlaType', {
    'code': fields.List(required=True, cls_or_instance=fields.String),
    'raw_code': fields.String(required=True),
})

HLATyping = patient_api.model('HlaTyping', {
    'hla_types_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAType)),
    'codes': fields.List(required=True, cls_or_instance=fields.String),
})

HLAAntibodies = patient_api.model('HlaAntibodies', {
    'hla_antibodies_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAAntibody)),
    'hla_codes_over_cutoff': fields.List(required=True, cls_or_instance=fields.String),
})

PatientParametersModel = patient_api.model('PatientParameters', {
    'blood_group': fields.String(required=False, enum=BLOOD_TYPES),
    'hla_typing': fields.List(required=False, cls_or_instance=fields.Nested(HLATyping)),
    'country_code': fields.String(required=False),
    'sex': fields.String(required=False, enum=[sex.name for sex in Sex]),
    'height': fields.Integer(required=False),
    'weight': fields.Float(required=False),
    'year_of_birth': fields.Integer(required=False),
})

RecipientRequirements = patient_api.model('RecipientRequirements', {
    'require_better_match_in_compatibility_index': fields.Boolean(required=True),
    'require_better_match_in_compatibility_index_or_blood_group': fields.Boolean(required=True),
    'require_compatible_blood_group': fields.Boolean(required=True)
})

DonorModel = patient_api.model('Donor model', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersModel),
    'donor_type': fields.String(required=True, enum=[donor_type.name for donor_type in DonorType]),
    'related_recipient_db_id': fields.Integer(required=False, description='Database id of the related recipient'),
})

RecipientModel = patient_api.model('RecipientModel', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_TYPES)),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersModel),
    'hla_antibodies': fields.Nested(required=True, model=HLAAntibodies),
    'related_donor_db_id': fields.Integer(required=True, description='Database id of the related donor'),
    'recipient_requirements': fields.Nested(RecipientRequirements),
    'waiting_since': fields.DateTime(required=False),
    'previous_transplants': fields.Integer(required=False),
})

PatientsModel = patient_api.model('Patients', {
    'recipients': fields.List(required=False, cls_or_instance=fields.Nested(RecipientModel)),
    'donors': fields.List(required=False, cls_or_instance=fields.Nested(DonorModel))
})

HLAAntibodyToUpdate = patient_api.model('HlaAntibodyToUpdate', {
    'raw_code': fields.String(required=True),
    'mfi': fields.Integer(required=True),
})

HLATypeToUpdate = patient_api.model('HlaTypeToUpdate', {
    'raw_code': fields.String(required=True),
})

HLATypingToUpdate = patient_api.model('HlaTypingToUpdate', {
    'hla_types_list': fields.List(required=True, cls_or_instance=fields.Nested(HLATypeToUpdate)),
})

HLAAntibodiesToUpdate = patient_api.model('HlaAntibodiesToUpdate', {
    'hla_antibodies_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAAntibodyToUpdate)),
})

RecipientModelToUpdate = patient_api.model('RecipientModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_TYPES),
                                           description='Provide full list of all the acceptable blood groups of the '
                                                       'patient, not just the change set'),
    'hla_typing': fields.Nested(HLATypingToUpdate, required=False,
                                description='Provide full list of all the HLA types of the patient, not just '
                                            'the change set'),
    'hla_antibodies': fields.Nested(HLAAntibodiesToUpdate, required=False,
                                    description='Provide full list of all the HLA antibodies of the patient, not just '
                                                'the change set'),
    'recipient_requirements': fields.Nested(RecipientRequirements, required=False,
                                            description='Provide the whole recipients requirements object, it will be'
                                                        ' overwritten'),
    'cutoff': fields.Integer(required=False)
})

DonorModelToUpdate = patient_api.model('DonorModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'hla_typing': fields.Nested(HLATypingToUpdate, required=False,
                                description='Provide full list of all the HLA types of the patient, not just '
                                            'the change set'),
})
