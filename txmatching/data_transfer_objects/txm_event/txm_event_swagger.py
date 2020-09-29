from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Country, Sex
from txmatching.web.api.namespaces import txm_event_api

# remove in task https://trello.com/c/pKMqnv7X
BLOOD_GROUPS = ['A', 'B', '0', 'AB']
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
    'name': fields.String(required=True, example='A32', description='HLA antibody name.'),
    'MFI': fields.Integer(required=True, example=2350, description='Mean fluorescence intensity. Use exact value.'),
    'cutoff': fields.Integer(required=True,
                             example=2000,
                             description='Default cutoff value for the specific patient and HLA antibody.'),
})

DonorJsonIn = txm_event_api.model('DonorInput', {
    'medical_id': fields.String(required=True, example='D1037', description=MEDICAL_ID_DESCRIPTION),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'HLA_typing': fields.List(required=True, cls_or_instance=fields.String,
                              example=ANTIGENS_EXAMPLE, description=HLA_TYPING_DESCRIPTION),
    'donor_type': fields.String(required=True, enum=[donor_type.name for donor_type in DonorType]),
    'related_recipient_medical_id': fields.String(required=False, example='R1037',
                                                  description='Medical ID of the related recipient, empty for bridging '
                                                              'and non-directed donors.'),
    'sex': fields.String(required=False, description='Sex of the patient.', enum=[sex.name for sex in Sex]),
    'height': fields.Integer(required=False, example=178, description='Height of the patient in centimeters.'),
    'weight': fields.Float(required=False, example=78.4, description='Weight of the patient in kilograms.'),
    'YOB': fields.Integer(required=False, example=1945, description='Year of birth of the patient.'),
})

RecipientJsonIn = txm_event_api.model('RecipientInput', {
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_GROUPS),
                                           description='Acceptable blood groups for the patient. Leave empty to use \
                                            compatible blood groups.'),
    'medical_id': fields.String(required=True, example='R1037', description=MEDICAL_ID_DESCRIPTION),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'HLA_typing': fields.List(required=True, cls_or_instance=fields.String,
                              example=ANTIGENS_EXAMPLE,
                              description=HLA_TYPING_DESCRIPTION),
    'HLA_antibodies': fields.List(required=True,
                                  description='Detected HLA antibodies of the patient. Use high resolution \
                                  if available.',
                                  cls_or_instance=fields.Nested(
                                      HlaAntibodiesJson
                                  )),
    'sex': fields.String(required=False, description='Sex of the patient.', enum=[sex.name for sex in Sex]),
    'height': fields.Integer(required=False, example=178, description='Height of the patient in centimeters.'),
    'weight': fields.Float(required=False, example=78.4, description='Weight of the patient in kilograms.'),
    'YOB': fields.Integer(required=False, example=1945, description='Year of birth of the patient.'),
    'waiting_since': fields.String(required=False,
                                   example='2015-01-17',
                                   description='Date since when the patient has been on waiting list. '
                                               'Use format YYYY-MM-DD.'),
    'previous_transplants': fields.Integer(required=False,
                                           example=0,
                                           description='Number of previous kidney transplants.'),
})

UploadPatientsJson = txm_event_api.model(
    'UploadPatients',
    {
        'country': fields.String(required=True, enum=[country.name for country in Country]),
        'TXM_event_name': fields.String(required=True,
                                        example='2020-10-CZE-IL-AUT',
                                        description='The TXM event name has to be provided by an ADMIN.'),
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
    'recipients_uploaded': fields.Integer(required=True,
                                          description='Number of recipients successfully loaded into the application.'),
    'donors_uploaded': fields.Integer(required=True,
                                      description='Number of donors successfully loaded into the application.'),
})
