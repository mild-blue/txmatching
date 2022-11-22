from flask_restx import fields

from txmatching.data_transfer_objects.enums_swagger import (BloodGroupEnumJson,
                                                            CountryCodeJson,
                                                            DonorTypeEnumJson,
                                                            SexEnumJson)
from txmatching.data_transfer_objects.hla.hla_swagger import (
    EXAMPLE_HLA_TYPING, HLATyping)
from txmatching.data_transfer_objects.hla.parsing_issue_swagger import ParsingIssueJson
from txmatching.utils.blood_groups import BloodGroup
from txmatching.web.web_utils.namespaces import patient_api, public_api

ANTIGENS_EXAMPLE = ['A1', 'A32', 'B7', 'B51', 'DR11', 'DR15', 'A*02:03', 'A*11:01:35', 'DPA1*01:07', 'DRB4*01:01',
                    'DQB1*02:01:01:01']

ANTIBODIES_EXAMPLE = ['A1', 'A32', 'B7', 'B51', 'DR11', 'DR15', 'A*02:03', 'A*11:01:35', 'DRB4*01:01',
                      'DP[02:01,02:01]', 'DQ[02:01,02:01]']
MEDICAL_ID_DESCRIPTION = 'Medical ID of the patient. This ID is unique thorough the system and can be used for the \
identification of a specific patient in your system. Typically, this is the patient ID used in your internal system.'
HLA_TYPING_DESCRIPTION = 'HLA typing of the patient. Use high resolution if available.'

DbId = {
    'db_id': fields.Integer(required=True, description='Database id of the patient', example=1),
}

Etag = {
    'etag': fields.Integer(required=True, description='Number of updates of a patient', example=1),
}

MedicalId = {
    'medical_id': fields.String(required=True, example='D1037', description=MEDICAL_ID_DESCRIPTION),
}

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

PatientParametersJson = patient_api.model('PatientParameters', {
    'blood_group': fields.Nested(BloodGroupEnumJson, required=True),
    'hla_typing': fields.Nested(required=False, model=HLATyping),
    'country_code': fields.Nested(CountryCodeJson, required=True),
    'sex': fields.Nested(SexEnumJson, required=False),
    'height': fields.Integer(required=False),
    'weight': fields.Float(required=False),
    'year_of_birth': fields.Integer(required=False),
    'note': fields.String(required=True, example='patient note'),
})

RecipientRequirements = patient_api.model('RecipientRequirements', {
    'require_better_match_in_compatibility_index': fields.Boolean(required=True),
    'require_better_match_in_compatibility_index_or_blood_group': fields.Boolean(required=True),
    'require_compatible_blood_group': fields.Boolean(required=True),
    'max_donor_weight': fields.Float(required=False),
    'min_donor_weight': fields.Float(required=False),
    'max_donor_height': fields.Integer(required=False),
    'min_donor_height': fields.Integer(required=False),
    'max_donor_age': fields.Integer(required=False),
    'min_donor_age': fields.Integer(required=False)
})

HLAAntibodyJsonIn = public_api.model('HLAAntibodyIn', {
    'name': fields.String(required=True, example='A*01:01',
                          description='HLA antibody name in high (A\\*01:01), low (A\\*01), split (A1) or broad (A9) '
                                      'resolutions. In case of DP or DQ, when alpha and beta are provided, the expected'
                                      ' format is DQ[01:01,02:02] equivalently DP[01:01,02:02], and will result in two '
                                      'separate antibodies. Alternatively, the antibodies can be provided separately, '
                                      'e.g., DQA*01:01 and DQB*02:02.'),
    'mfi': fields.Integer(required=True, example=2350, description='Mean fluorescence intensity. Use exact value.'),
    'cutoff': fields.Integer(required=True,
                             example=2000,
                             description='Default cutoff value for the specific patient and HLA antibody.'),
})

BasePatient = {
    'blood_group': fields.Nested(BloodGroupEnumJson, required=True),
    'sex': fields.Nested(SexEnumJson, required=False),
    'height': fields.Integer(required=False, example=178, description='Height of the patient in centimeters.'),
    'weight': fields.Float(required=False, example=78.4, description='Weight of the patient in kilograms.'),
    'year_of_birth': fields.Integer(required=False, example=1945, description='Year of birth of the patient.'),
    'note': fields.String(required=False, example='donor note', default=''),
}

NewPatient = {**BasePatient, **MedicalId, **{
    'internal_medical_id': fields.String(required=False,
                                         example='123456',
                                         description='Custom medical ID that will not be shown in UI, but will be'
                                                     ' stored and can be seen in patient xlsx export.'),
    'hla_typing': fields.List(required=True, cls_or_instance=fields.String,
                              example=ANTIGENS_EXAMPLE, description=HLA_TYPING_DESCRIPTION),
}}

PatientToUpdate = {**DbId, **BasePatient, **Etag, **{
    'hla_typing': fields.Nested(HLATypingToUpdateJson, required=False,
                                description='Provide full list of all the HLA types of the patient, not just '
                                            'the change set',
                                example=EXAMPLE_HLA_TYPING)
}}

NewDonor = {
    'donor_type': fields.Nested(DonorTypeEnumJson,
                                required=True),
    'related_recipient_medical_id': fields.String(
        required=False, example='R1037',
        description='Medical ID of the related recipient, empty for bridging '
                    'and non-directed donors.'),
}

DonorToUpdate = {
    'active': fields.Boolean(required=False, description='Information, whether or not given donor shall be considered'
                                                         ' in exchange.')}

BaseRecipient = {
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.Nested(BloodGroupEnumJson),
                                           description='Acceptable blood groups for the patient. Leave empty to use '
                                                       'compatible blood groups.',
                                           example=[BloodGroup.A.value, BloodGroup.ZERO.value]),
    'waiting_since': fields.Date(required=False,
                                 example='2015-01-17',
                                 description='Date since when the patient has been on waiting list. '
                                             'Use format YYYY-MM-DD.'),
    'previous_transplants': fields.Integer(required=False,
                                           example=0,
                                           description='Number of previous kidney transplants.'),
}

NewRecipient = {**BaseRecipient, **{
    'hla_antibodies': fields.List(required=True,
                                  description='Detected HLA antibodies of the patient. Use high resolution '
                                              'if available. If high resolution is provided it is assumed that all'
                                              ' tested antibodies were provided. If not it is assumed that either '
                                              'all or just positive ones were.',
                                  cls_or_instance=fields.Nested(
                                      HLAAntibodyJsonIn
                                  ))
}}

RecipientToUpdate = {**BaseRecipient, **{
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
}}

AllMessagesJson = patient_api.model('AllMessages', {
    'infos': fields.List(
        required=False,
        cls_or_instance=fields.Nested(ParsingIssueJson)
    ),
    'warnings': fields.List(
        required=False,
        cls_or_instance=fields.Nested(ParsingIssueJson)
    ),
    'errors': fields.List(
        required=False,
        cls_or_instance=fields.Nested(ParsingIssueJson)
    )
})
