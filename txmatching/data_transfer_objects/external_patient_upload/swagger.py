from flask_restx import fields

from txmatching.data_transfer_objects.base_patient_swagger import (
    NewDonor, NewPatient, NewRecipient, ANTIGENS_EXAMPLE, HLA_TYPING_DESCRIPTION, HLAAntibodyJsonIn)
from txmatching.data_transfer_objects.enums_swagger import CountryCodeJson, StrictnessTypeEnumJson
from txmatching.data_transfer_objects.hla.parsing_issue_swagger import \
    ParsingIssuePublicJson, ParsingIssueBaseJson
from txmatching.utils.enums import HLA_GROUPS, AntibodyMatchTypes
from txmatching.web.web_utils.namespaces import public_api

PatientUploadSuccessJson = public_api.model('PatientUploadSuccessResponse', {
    'recipients_uploaded': fields.Integer(required=True,
                                          description='Number of recipients successfully loaded into the application.'),
    'donors_uploaded': fields.Integer(required=True,
                                      description='Number of donors successfully loaded into the application.'),
    'parsing_issues': fields.List(required=True,
                                  cls_or_instance=fields.Nested(ParsingIssuePublicJson),
                                  description='Errors and warnings that occurred in HLA codes parsing'),
})

DonorJsonIn = public_api.model('DonorInput', {**NewPatient, **NewDonor})

RecipientJsonIn = public_api.model('RecipientInput', {**NewPatient, **NewRecipient})

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
                                                               ' currently uploaded data.'),
        'strictness_type': fields.Nested(StrictnessTypeEnumJson, required=False)
    }
)

CopyPatientsJsonOut = public_api.model(
    'CopyPatients',
    {
        'new_donor_ids': fields.List(required=True, cls_or_instance=fields.Integer)
    }
)

HLACode = public_api.model('HlaCode', {
    'high_res': fields.String(required=False),
    'split': fields.String(required=False),
    'broad': fields.String(required=True),
    'group': fields.String(required=False, enum=[group.name for group in HLA_GROUPS]),
})

HLAAntibody = public_api.model('HlaAntibody', {
    'raw_code': fields.String(required=True),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.Integer(required=True),
    'code': fields.Nested(HLACode, required=True)
})

AntibodyMatchJson = public_api.model('AntibodyMatch', {
    'hla_antibody': fields.Nested(required=True, model=HLAAntibody),
    'match_type': fields.String(required=True, enum=[match_type.name for match_type in AntibodyMatchTypes])
})

AntibodyMatchForHLAGroupJson = public_api.model('AntibodyMatchForHLAGroup', {
    'hla_group': fields.String(required=True, enum=[group.name for group in HLA_GROUPS]),
    'antibody_matches': fields.List(required=True, cls_or_instance=fields.Nested(AntibodyMatchJson)),
})

CrossmatchJsonIn = public_api.model(
    'CrossmatchInput',
    {
        'donor_hla_typing': fields.List(required=True, cls_or_instance=fields.String,
                                        example=ANTIGENS_EXAMPLE, description=HLA_TYPING_DESCRIPTION),
        'recipient_antibodies': fields.List(required=True,
                                            description='Detected HLA antibodies of the patient. Use high resolution '
                                                        'if available. If high resolution is provided it is assumed that all'
                                                        ' tested antibodies were provided. If not it is assumed that either '
                                                        'all or just positive ones were.',
                                            cls_or_instance=fields.Nested(
                                                HLAAntibodyJsonIn
                                            ))
    }
)

CrossmatchJsonOut = public_api.model(
    'CrossmatchOutput',
    {
        'crossmatched_antibodies_per_group': fields.List(required=True,
                                                         cls_or_instance=fields.Nested(AntibodyMatchForHLAGroupJson)),
        'parsing_issues': fields.List(required=True, cls_or_instance=fields.Nested(ParsingIssueBaseJson))
    }
)
