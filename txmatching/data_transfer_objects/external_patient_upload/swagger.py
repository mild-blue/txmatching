from flask_restx import fields

from txmatching.data_transfer_objects.enums_swagger import (BloodGroupEnumJson,
                                                            CountryCodeJson,
                                                            DonorTypeEnumJson,
                                                            SexEnumJson)
from txmatching.data_transfer_objects.hla.parsing_error_swagger import \
    ParsingErrorJson
from txmatching.utils.blood_groups import BloodGroup
from txmatching.web.web_utils.namespaces import public_api

PatientUploadSuccessJson = public_api.model('PatientUploadSuccessResponse', {
    'recipients_uploaded': fields.Integer(required=True,
                                          description='Number of recipients successfully loaded into the application.'),
    'donors_uploaded': fields.Integer(required=True,
                                      description='Number of donors successfully loaded into the application.'),
    'parsing_errors': fields.List(required=True,
                                  cls_or_instance=fields.Nested(ParsingErrorJson),
                                  description='Errors and warnings that occurred in HLA codes parsing'),
})

ANTIGENS_EXAMPLE = ['A1', 'A32', 'B7', 'B51', 'DR11', 'DR15', 'A*02:03', 'A*11:01:35', 'DPA1*01:07', 'DRB4*01:01',
                    'DQB1*02:01:01:01']

ANTIBODIES_EXAMPLE = ['A1', 'A32', 'B7', 'B51', 'DR11', 'DR15', 'A*02:03', 'A*11:01:35', 'DRB4*01:01',
                      'DP[02:01,02:01]', 'DQ[02:01,02:01]']
MEDICAL_ID_DESCRIPTION = 'Medical ID of the patient. This ID is unique thorough the system and can be used for the \
identification of a specific patient in your system. Typically, this is the patient ID used in your internal system.'
HLA_TYPING_DESCRIPTION = 'HLA typing of the patient. Use high resolution if available.'

HLAAntibodyJsonIn = public_api.model('HLAAntibodyIn', {
    'name': fields.String(required=True, example='A*01:01',
                          description='HLA antibody name in high (A\\*01:01), low (A\\*01), split (A1) or broad (A9) '
                                      'resolutions. In case of DP or DQ, when alpha and beta are provided, the expected'
                                      ' format is DQ[01:01,02:02]'),
    'mfi': fields.Integer(required=True, example=2350, description='Mean fluorescence intensity. Use exact value.'),
    'cutoff': fields.Integer(required=True,
                             example=2000,
                             description='Default cutoff value for the specific patient and HLA antibody.'),
})

DonorJsonIn = public_api.model('DonorInput', {
    'medical_id': fields.String(required=True, example='D1037', description=MEDICAL_ID_DESCRIPTION),
    'blood_group': fields.Nested(BloodGroupEnumJson, required=True),
    'hla_typing': fields.List(required=True, cls_or_instance=fields.String,
                              example=ANTIGENS_EXAMPLE, description=HLA_TYPING_DESCRIPTION),
    'donor_type': fields.Nested(DonorTypeEnumJson, required=True),
    'related_recipient_medical_id': fields.String(required=False, example='R1037',
                                                  description='Medical ID of the related recipient, empty for bridging '
                                                              'and non-directed donors.'),
    'sex': fields.Nested(SexEnumJson, required=False),
    'height': fields.Integer(required=False, example=178, description='Height of the patient in centimeters.'),
    'weight': fields.Float(required=False, example=78.4, description='Weight of the patient in kilograms.'),
    'year_of_birth': fields.Integer(required=False, example=1945, description='Year of birth of the patient.'),
    'note': fields.String(required=False, example='donor note', default=''),
    'internal_medical_id': fields.String(required=False,
                                         example='123456',
                                         description='Custom medical ID that will not be shown in UI, but will be'
                                                     ' stored and can be seen in patient xlsx export.'),
})

RecipientJsonIn = public_api.model('RecipientInput', {
    'hla_antibodies': fields.List(required=True,
                                  description='Detected HLA antibodies of the patient. Use high resolution \
                                  if available. If high resolution is provided it is assumed that all tested antibodies'
                                              ' were provided. If not it is assumed that either all or just positive'
                                              ' ones were.',
                                  cls_or_instance=fields.Nested(
                                      HLAAntibodyJsonIn
                                  )),
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.Nested(BloodGroupEnumJson),
                                           description='Acceptable blood groups for the patient. Leave empty to use \
                                            compatible blood groups.',
                                           example=[BloodGroup.A.value, BloodGroup.ZERO.value]),
    'medical_id': fields.String(required=True, example='R1037', description=MEDICAL_ID_DESCRIPTION),
    'blood_group': fields.Nested(BloodGroupEnumJson, required=True),
    'hla_typing': fields.List(required=True, cls_or_instance=fields.String,
                              example=ANTIGENS_EXAMPLE,
                              description=HLA_TYPING_DESCRIPTION),

    'sex': fields.Nested(SexEnumJson, required=False),
    'height': fields.Integer(required=False, example=178, description='Height of the patient in centimeters.'),
    'weight': fields.Float(required=False, example=78.4, description='Weight of the patient in kilograms.'),
    'year_of_birth': fields.Integer(required=False, example=1945, description='Year of birth of the patient.'),
    'note': fields.String(required=False, example='recipient note', default=''),
    'waiting_since': fields.Date(required=False,
                                 example='2015-01-17',
                                 description='Date since when the patient has been on waiting list. '
                                             'Use format YYYY-MM-DD.'),
    'previous_transplants': fields.Integer(required=False,
                                           example=0,
                                           description='Number of previous kidney transplants.'),
    'internal_medical_id': fields.String(required=False,
                                         example='123456',
                                         description='Custom medical ID that will not be shown in UI, but will be'
                                                     ' stored and can be seen in patient xlsx export.'),
})

UploadPatientsJson = public_api.model(
    'UploadPatients',
    {
        'country': fields.Nested(CountryCodeJson, required=True),
        'txm_event_name': fields.String(required=True,
                                        example='2020-10-example_event',
                                        description='The TXM event name has to be provided by an ADMIN.'),
        'donors': fields.List(required=True, cls_or_instance=fields.Nested(
            DonorJsonIn
        )),
        'recipients': fields.List(required=True, cls_or_instance=fields.Nested(
            RecipientJsonIn
        )),
        'add_to_existing_patients': fields.Boolean(required=False, default=False,
                                                   description='If *true* the currently uploaded patients will be added'
                                                               ' to the patients already in the system. If *false* the'
                                                               ' data in the system will be overwritten by the'
                                                               ' currently uploaded data.')
    }
)
