from flask_restx import fields

from txmatching.data_transfer_objects.matchings.matching_swagger import (
    DESCRIPTION_DETAILED_SCORE, EXAMPLE_DETAILED_SCORE, DetailedScoreForGroup)
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import (HLA_GROUPS_NAMES_WTIH_OTHER,
                                    HLA_OTHER_GROUPS_NAME, Country, HLAGroups,
                                    Sex)
from txmatching.web.api.namespaces import patient_api

HLA_CODES_IN_GROUPS_EXAMPLE = [
    {'hla_group': HLAGroups.A.name,
     'hla_codes': ['A1']},
    {'hla_group': HLAGroups.B.name,
     'hla_codes': ['B38']},
    {'hla_group': HLAGroups.DRB1.name,
     'hla_codes': ['DR7']},
    {'hla_group': HLA_OTHER_GROUPS_NAME,
     'hla_codes': ['CW4']}
]

EXAMPLE_HLA_TYPING = {'hla_types_list': [{'raw_code': 'A*01:02'},
                                         {'raw_code': 'B7'},
                                         {'raw_code': 'DR11'}]}

HlaCodesInGroup = patient_api.model('HlaCodesInGroups', {
    'hla_group': fields.String(required=True, enum=[group for group in HLA_GROUPS_NAMES_WTIH_OTHER]),
    'hla_codes': fields.List(required=True, cls_or_instance=fields.String)
})

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
    'codes_per_group': fields.List(required=True,
                                   description='hla codes split to hla groups',
                                   example=HLA_CODES_IN_GROUPS_EXAMPLE,
                                   cls_or_instance=fields.Nested(HlaCodesInGroup)),
})

HLAAntibodies = patient_api.model('HlaAntibodies', {
    'hla_antibodies_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAAntibody)),
    'hla_codes_over_cutoff_per_group': fields.List(required=True,
                                                   description='hla codes split to hla groups',
                                                   example=HLA_CODES_IN_GROUPS_EXAMPLE,
                                                   cls_or_instance=fields.Nested(HlaCodesInGroup)),
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
    'score_with_related_recipient': fields.Float(required=False, description='Score calculated with related recipient'),
    'detailed_compatibility_index_with_related_recipient': fields.List(
        required=False,
        description=DESCRIPTION_DETAILED_SCORE,
        example=EXAMPLE_DETAILED_SCORE,
        cls_or_instance=fields.Nested(DetailedScoreForGroup)),
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
    'raw_code': fields.String(required=True, example='A*01:02'),
    'mfi': fields.Integer(required=True, example=10000),
})

HLATypeToUpdate = patient_api.model('HlaTypeToUpdate', {
    'raw_code': fields.String(required=True, example='A*01:02'),
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
                                example=EXAMPLE_HLA_TYPING),
    'hla_antibodies': fields.Nested(HLAAntibodiesToUpdate, required=False,
                                    description='Provide full list of all the HLA antibodies of the patient, not just '
                                                'the change set',
                                    example={'hla_antibodies_list': [
                                        {
                                            'raw_code': 'A*01:02',
                                            'mfi': 10000
                                        }
                                    ]}),
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
                                example=EXAMPLE_HLA_TYPING),
    'active': fields.Boolean(required=False, description='Information, whether or not given donor shall be considered'
                                                         ' in exchange.')
})
