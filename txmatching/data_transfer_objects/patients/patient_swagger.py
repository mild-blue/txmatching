from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex
from txmatching.web.api.namespaces import patient_api

HLAAntibody = patient_api.model('HlaAntibody', {
    'raw_code': fields.String(required=True),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.Integer(required=True),
    'code': fields.String(required=False)
})

HLAType = patient_api.model('HlaType', {
    'code': fields.String(required=False),
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
    'blood_group': fields.String(required=False, enum=[blood_group.value for blood_group in BloodGroup]),
    'hla_typing': fields.Nested(required=False, model=HLATyping),
    'country_code': fields.String(required=False, enum=[country.value for country in Country]),
    'sex': fields.String(required=False, enum=[sex.value for sex in Sex]),
    'height': fields.Integer(required=False),
    'weight': fields.Float(required=False),
    'year_of_birth': fields.Integer(required=False),
})

RecipientRequirements = patient_api.model('RecipientRequirements', {
    'require_better_match_in_compatibility_index': fields.Boolean(required=True),
    'require_better_match_in_compatibility_index_or_blood_group': fields.Boolean(required=True),
    'require_compatible_blood_group': fields.Boolean(required=True)
})

DonorModel = patient_api.model('DonorModel', {
    'active': fields.Boolean(required=True, description='Whether the user shall be used in pairing calculation'),
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersModel),
    'donor_type': fields.String(required=True, enum=[donor_type.value for donor_type in DonorType]),
    'related_recipient_db_id': fields.Integer(required=False, description='Database id of the related recipient'),
})

RecipientModel = patient_api.model('RecipientModel', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(
        enum=[blood_group.value for blood_group in BloodGroup])),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersModel),
    'hla_antibodies': fields.Nested(required=True, model=HLAAntibodies),
    'related_donor_db_id': fields.Integer(required=True, description='Database id of the related donor'),
    'recipient_requirements': fields.Nested(RecipientRequirements),
    'waiting_since': fields.DateTime(required=False),
    'previous_transplants': fields.Integer(required=False),
    'recipient_cutoff': fields.Integer(required=False)
})

PatientsModel = patient_api.model('Patients', {
    'recipients': fields.List(required=False, cls_or_instance=fields.Nested(RecipientModel)),
    'donors': fields.List(required=False, cls_or_instance=fields.Nested(DonorModel))
})

HLAAntibodyToUpdate = patient_api.model('HlaAntibodyToUpdate', {
    'raw_code': fields.String(required=True, example='A1'),
    'mfi': fields.Integer(required=True, example=10000),
})

HLATypeToUpdate = patient_api.model('HlaTypeToUpdate', {
    'raw_code': fields.String(required=True, example='A1'),
})

HLATypingToUpdate = patient_api.model('HlaTypingToUpdate', {
    'hla_types_list': fields.List(required=True, cls_or_instance=fields.Nested(HLATypeToUpdate)),
})

HLAAntibodiesToUpdate = patient_api.model('HlaAntibodiesToUpdate', {
    'hla_antibodies_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAAntibodyToUpdate)),
})

RecipientModelToUpdate = patient_api.model('RecipientModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient', example=1),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(
        enum=[blood_group.value for blood_group in BloodGroup]),
                                           description='Provide full list of all the acceptable blood groups of the '
                                                       'patient, not just the change set'),
    'hla_typing': fields.Nested(HLATypingToUpdate, required=False,
                                description='Provide full list of all the HLA types of the patient, not just '
                                            'the change set',
                                example={'hla_types_list': [{'raw_code': 'A1'}]}),
    'hla_antibodies': fields.Nested(HLAAntibodiesToUpdate, required=False,
                                    description='Provide full list of all the HLA antibodies of the patient, not just '
                                                'the change set',
                                    example={'hla_antibodies_list': [{
                                        'raw_code': 'A1',
                                        'mfi': 10000
                                    }]
                                    }
                                    ),
    'recipient_requirements': fields.Nested(RecipientRequirements, required=False,
                                            description='Provide the whole recipients requirements object, it will be'
                                                        ' overwritten',
                                            example={'require_better_match_in_compatibility_index': True}),
    'cutoff': fields.Integer(required=False)
})

DonorModelToUpdate = patient_api.model('DonorModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient', example=1),
    'hla_typing': fields.Nested(HLATypingToUpdate, required=False,
                                description='Provide full list of all the HLA types of the patient, not just '
                                            'the change set',
                                example={'hla_types_list': [{'raw_code': 'A1'}]}),
    'active': fields.Boolean(required=False, description='Information, whether or not given donor shall be considered'
                                                         ' in exchange.')
})
