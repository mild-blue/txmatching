from flask_restx import fields

from txmatching.patients.patient import DonorType
from txmatching.utils.country import Country
from txmatching.web.api.namespaces import tx_session_api

# remove in task https://trello.com/c/pKMqnv7X
BLOOD_GROUPS = ['A', 'B', '0', 'AB']
ANTIGENS_EXAMPLE = ['A1', 'A32', 'B7', 'B51', 'DR11','DR15']

TX_SESSION_JSON_IN = tx_session_api.model('New Tx session', {
    'name': fields.String(required=True)
})

TX_SESSION_JSON_OUT = tx_session_api.model('New Tx session', {
    'name': fields.String(required=True),
    'db_id': fields.Integer(required=True),
})


HLA_ANTIBODIES_MODEL = tx_session_api.model('Hla Antibodies', {
    'MFI': fields.Integer(required=True, description='Mean fluorescence intensity', example=2350),
    'name': fields.String(required=True, description='HLA antigen name', example='A32'),
}
)

DONOR_MODEL = tx_session_api.model('Donor', {
    'medical_id': fields.String(required=True, description='Medical id of the patient', example='DonorId'),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'hla_antigens': fields.List(required=True, cls_or_instance=fields.String, example=ANTIGENS_EXAMPLE),
    'donor_type': fields.String(required=True, enum=[donor_type.name for donor_type in DonorType]),
    'related_recipient_medical_id': fields.String(required=False,
    example='RelatedRecipientId',
     description='Medical id of the related recipient, empty for bridging donors and altruists'),
})

RECIPIENT_MODEL = tx_session_api.model('Recipient', {
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.String(enum=BLOOD_GROUPS),
                                           description='Acceptable blood groups for the patient, if empty, compatible \
                                            blood groups are used.'),
    'medical_id': fields.String(required=True, description='Medical id of the patient', example='RecipientId'),
    'blood_group': fields.String(required=True, enum=BLOOD_GROUPS),
    'hla_antigens': fields.List(required=True, cls_or_instance=fields.String, example=ANTIGENS_EXAMPLE),
    'hla_antibodies': fields.List(required=True, cls_or_instance=fields.Nested(
        HLA_ANTIBODIES_MODEL
    ))
})


UPLOAD_PATIENTS_JSON = tx_session_api.model(
    'Upload patients',
    {
        'country': fields.String(required=True, enum=[country.name for country in Country]),
        'tx_session_name': fields.String(required=True, example='10-2020'),
        'donors': fields.List(required=True, cls_or_instance=fields.Nested(
            DONOR_MODEL
        )),
        'recipients': fields.List(required=True, cls_or_instance=fields.Nested(
            RECIPIENT_MODEL
        ))
    }
)
