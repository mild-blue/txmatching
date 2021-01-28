from flask_restx import fields

from txmatching.data_transfer_objects.hla.hla_swagger import (
    EXAMPLE_HLA_TYPING, HLAAntibodies, HLATyping)
from txmatching.data_transfer_objects.matchings.matching_swagger import (
    DESCRIPTION_DETAILED_SCORE, EXAMPLE_DETAILED_SCORE,
    DetailedScoreForGroupJson)
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    RECIPIENT_IN_BASE_DICT, DonorJsonIn)
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex
from txmatching.web.api.namespaces import patient_api

PatientParametersJson = patient_api.model('PatientParameters', {
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

DonorJson = patient_api.model('Donor', {
    'active': fields.Boolean(required=True, description='Whether the user shall be used in pairing calculation'),
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersJson),
    'donor_type': fields.String(required=True, enum=[donor_type.value for donor_type in DonorType]),
    'related_recipient_db_id': fields.Integer(required=False, description='Database id of the related recipient'),
    'score_with_related_recipient': fields.Float(required=False, description='Score calculated with related recipient'),
    'compatible_blood_with_related_recipient': fields.Boolean(
        required=False,
        description='Indicator whether Donor and related recipients have compatible blood groups'
    ),
    'detailed_score_with_related_recipient': fields.List(
        required=False,
        description=DESCRIPTION_DETAILED_SCORE,
        example=EXAMPLE_DETAILED_SCORE,
        cls_or_instance=fields.Nested(DetailedScoreForGroupJson)),
})

RecipientJson = patient_api.model('Recipient', {
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(
        enum=[blood_group.value for blood_group in BloodGroup])),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersJson),
    'hla_antibodies': fields.Nested(required=True, model=HLAAntibodies),
    'related_donor_db_id': fields.Integer(required=True, description='Database id of the related donor'),
    'recipient_requirements': fields.Nested(RecipientRequirements),
    'waiting_since': fields.DateTime(required=False),
    'previous_transplants': fields.Integer(required=False),
    'recipient_cutoff': fields.Integer(required=False)
})

PatientsJson = patient_api.model('Patients', {
    'recipients': fields.List(required=False, cls_or_instance=fields.Nested(RecipientJson)),
    'donors': fields.List(required=False, cls_or_instance=fields.Nested(DonorJson))
})

HLAAntibodyToUpdateJson = patient_api.model('HlaAntibodyToUpdate', {
    'raw_code': fields.String(required=True, example='A*01:02'),
    'mfi': fields.Integer(required=True, example=10000),
})

HLATypeToUpdateJson = patient_api.model('HlaTypeToUpdate', {
    'raw_code': fields.String(required=True, example='A*01:02'),
})

HLATypingToUpdateJson = patient_api.model('HlaTypingToUpdate', {
    'hla_types_list': fields.List(required=True, cls_or_instance=fields.Nested(HLATypeToUpdateJson)),
})

HLAAntibodiesToUpdateJson = patient_api.model('HlaAntibodiesToUpdate', {
    'hla_antibodies_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAAntibodyToUpdateJson)),
})

RecipientModelToUpdateJson = patient_api.model('RecipientModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient', example=1),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(
        enum=[blood_group.value for blood_group in BloodGroup]),
                                           description='Provide full list of all the acceptable blood groups of the '
                                                       'patient, not just the change set'),
    'hla_typing': fields.Nested(HLATypingToUpdateJson, required=False,
                                description='Provide full list of all the HLA types of the patient, not just '
                                            'the change set',
                                example=EXAMPLE_HLA_TYPING),
    'hla_antibodies': fields.Nested(HLAAntibodiesToUpdateJson, required=False,
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

DonorModelToUpdateJson = patient_api.model('DonorModelToUpdate', {
    'db_id': fields.Integer(required=True, description='Database id of the patient', example=1),
    'hla_typing': fields.Nested(HLATypingToUpdateJson, required=False,
                                description='Provide full list of all the HLA types of the patient, not just '
                                            'the change set',
                                example=EXAMPLE_HLA_TYPING),
    'active': fields.Boolean(required=False, description='Information, whether or not given donor shall be considered'
                                                         ' in exchange.')
})

HLAAntibodyPairInJson = patient_api.model('HLAAntibodyPairIn', {
    'name': fields.String(required=True, example='A32', description='HLA antibody name.'),
    'mfi': fields.Integer(required=True, example=2350, description='Mean fluorescence intensity. Use exact value.'),
})
# pylint: disable=duplicate-code
# here the code is duplicated because the object RecipientPairInJson and RecipientJsonIn in txm_event_swagger are
# similar but they cannot be the same because some of the fileds are sim
RecipientPairInJson = patient_api.model('RecipientPairIn', {
    'recipient_cutoff': fields.Integer(required=True, example=4000),
    'hla_antibodies': fields.List(required=True,
                                  description='Detected HLA antibodies of the patient. Use high resolution \
                                  if available.',
                                  cls_or_instance=fields.Nested(
                                      HLAAntibodyPairInJson
                                  )),
    **RECIPIENT_IN_BASE_DICT
})

DonorModelPairInJson = patient_api.model('DonorModelPairIn', {
    'country_code': fields.String(required=False, enum=[country.value for country in Country]),
    'donor': fields.Nested(required=True, model=DonorJsonIn),
    'recipient': fields.Nested(required=False, model=RecipientPairInJson)
})
