from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.utils.country import Country
from txmatching.web.api.namespaces import txm_event_api

# remove in task https://trello.com/c/pKMqnv7X
BLOOD_GROUPS = ['A', 'B', '0', 'AB']
ANTIGENS_EXAMPLE = ['A1', 'A32', 'B7', 'B51', 'DR11', 'DR15']
MEDICAL_ID_DESCRIPTION = 'Medical ID of the patient. This ID is unique thorough the system and can be used for the \
identification of a specific patient in your system. Typically, this is the patient ID used in your internal system.'
HLA_TYPING_DESCRIPTION = 'HLA typing of the patient. Use high resolution if available.'

TxmEventJsonIn = txm_event_api.model('New TXM event', {
    'name': fields.String(required=True)
})

TxmEventJsonOut = txm_event_api.model('TXM event', {
    'name': fields.String(required=True),
    'db_id': fields.Integer(required=True),
})

HlaAntibodiesJson = txm_event_api.model('HLA Antibodies', {
    'MFI': fields.Integer(required=True, description='Mean fluorescence intensity. Use exact value.', example=2350),
    'name': fields.String(required=True, description='HLA antibody name', example='A32'),
})

DonorJsonIn = txm_event_api.model('Donor', {
    'medical_id': fields.String(required=True, description=MEDICAL_ID_DESCRIPTION, example='D1037'),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'hla_typing': fields.List(required=True, cls_or_instance=fields.String, description=HLA_TYPING_DESCRIPTION,
                              example=ANTIGENS_EXAMPLE),
    'donor_type': fields.String(required=True, enum=[donor_type.name for donor_type in DonorType]),
    'related_recipient_medical_id': fields.String(required=False, example='RelatedRecipientId',
                                                  description='Medical ID of the related recipient, empty for bridging '
                                                              'donors and altruists'),
})

RecipientJsonIn = txm_event_api.model('Recipient', {
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_GROUPS),
                                           description='Acceptable blood groups for the patient. Leave empty to use \
                                            compatible blood groups.'),
    'medical_id': fields.String(required=True, description=MEDICAL_ID_DESCRIPTION, example='R1037'),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'hla_typing': fields.List(required=True, cls_or_instance=fields.String,
                              description=HLA_TYPING_DESCRIPTION,
                              example=ANTIGENS_EXAMPLE),
    'hla_antibodies': fields.List(required=True,
                                  description='Detected HLA antibodies of the patient. Use high resolution \
                                  if available.',
                                  cls_or_instance=fields.Nested(
                                      HlaAntibodiesJson
                                  ))
})

UploadPatientsJson = txm_event_api.model(
    'Upload patients',
    {
        'country': fields.String(required=True, enum=[country.name for country in Country]),
        'txm_event_name': fields.String(required=True,
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

FailJson = txm_event_api.model('Fail Response', {
    'error': fields.String(required=True),
    'reason': fields.String(required=True),
})

PatientUploadSuccessJson = txm_event_api.model('Patient upload success Response', {
    'recipients_uploaded': fields.Integer(required=True),
    'donors_uploaded': fields.Integer(required=True),
})
