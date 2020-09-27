from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Country
from txmatching.web.api.namespaces import txm_event_api

# remove in task https://trello.com/c/pKMqnv7X
BLOOD_GROUPS = ['A', 'B', '0', 'AB']
SEXES = ['M', 'F']
ANTIGENS_EXAMPLE = ['A1', 'A32', 'B7', 'B51', 'DR11', 'DR15', 'A*02:03', 'A*11:01:35', 'DPA1*01:07', 'DRB4*01:01',
                    'DQB1*02:01:01:01']
MEDICAL_ID_DESCRIPTION = 'Medical ID of the patient. This ID is unique thorough the system and can be used for the \
identification of a specific patient in your system. Typically, this is the patient ID used in your internal system.'
HLA_TYPING_DESCRIPTION = 'HLA typing of the patient. Use high resolution if available.'

TxmEventJsonIn = txm_event_api.model('NewTxmEvent', {
    'name': fields.String(required=True)
})

TxmEventJsonOut = txm_event_api.model('TxmEvent', {
    'name': fields.String(required=True),
    'db_id': fields.Integer(required=True),
})

HlaAntibodiesJson = txm_event_api.model('HLAAntibodies', {
    'name': fields.String(required=True, description='HLA antibody name', example='A32'),
    'MFI': fields.Integer(required=True, description='Mean fluorescence intensity. Use exact value.', example=2350),
    'cutoff': fields.Integer(required=True,
                             description='Default cutoff value for the specific patient and HLA antibody.',
                             example=2000),
})

DonorJsonIn = txm_event_api.model('Donor', {
    'medical_id': fields.String(required=True, description=MEDICAL_ID_DESCRIPTION, example='D1037'),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'HLA_typing': fields.List(required=True, cls_or_instance=fields.String, description=HLA_TYPING_DESCRIPTION,
                              example=ANTIGENS_EXAMPLE),
    'donor_type': fields.String(required=True, enum=[donor_type.name for donor_type in DonorType]),
    'related_recipient_medical_id': fields.String(required=False, example='R1037',
                                                  description='Medical ID of the related recipient, empty for bridging '
                                                              'donors and non-directed.'),
    'sex': fields.String(required=True, description='Sex of patient', enum=SEXES),
    'height': fields.Integer(required=True, description='Height of the patient in centimeters.', example=178),
    'weight': fields.Float(required=True, description='Weight of the patient in kilograms.', example=78.4),
    'yob': fields.Integer(required=True, description='Year of birth of the patient.', example=1945),
})

RecipientJsonIn = txm_event_api.model('Recipient', {
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_GROUPS),
                                           description='Acceptable blood groups for the patient. Leave empty to use \
                                            compatible blood groups.'),
    'medical_id': fields.String(required=True, description=MEDICAL_ID_DESCRIPTION, example='R1037'),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'HLA_typing': fields.List(required=True, cls_or_instance=fields.String,
                              description=HLA_TYPING_DESCRIPTION,
                              example=ANTIGENS_EXAMPLE),
    'HLA_antibodies': fields.List(required=True,
                                  description='Detected HLA antibodies of the patient. Use high resolution \
                                  if available.',
                                  cls_or_instance=fields.Nested(
                                      HlaAntibodiesJson
                                  )),
    'sex': fields.String(required=True, description='Sex of patient', enum=SEXES),
    'height': fields.Integer(required=True, description='Height of the patient in centimeters.', example=178),
    'weight': fields.Float(required=True, description='Weight of the patient in kilograms.', example=78.4),
    'yob': fields.Integer(required=True, description='Year of birth of the patient.', example=1945),
    'waiting_since': fields.String(required=True,
                                   description='Date since when the patient has been on waiting list. '
                                               'Use format YYYY-MM-DD.',
                                   example='2015-01-17'),
    'previous_transplants': fields.Integer(required=True,
                                           description='Number of previous kidney transplants.',
                                           example=0),
})

UploadPatientsJson = txm_event_api.model(
    'Upload patients',
    {
        'country': fields.String(required=True, enum=[country.name for country in Country]),
        'TXM_event_name': fields.String(required=True,
                                        description='The TXM event name has to be provided by an ADMIN.',
                                        example='2020-10-CZE-IL-AUT'),
        'donors': fields.List(required=True, cls_or_instance=fields.Nested(
            DonorJsonIn
        )),
        'recipients': fields.List(required=True, cls_or_instance=fields.Nested(
            RecipientJsonIn
        ))
    }
)

FailJson = txm_event_api.model('FailResponse', {
    'error': fields.String(required=True),
    'reason': fields.String(required=False),
})

PatientUploadSuccessJson = txm_event_api.model('PatientUploadSuccessResponse', {
    'recipients_uploaded': fields.Integer(required=True),
    'donors_uploaded': fields.Integer(required=True),
})
