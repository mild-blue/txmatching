from flask_restx import fields

from txmatching.data_transfer_objects.base_patient_swagger import (
    NewDonor, NewPatient, NewRecipient, ANTIGENS_EXAMPLE, HLA_TYPING_DESCRIPTION, HLAAntibodyJsonIn)
from txmatching.data_transfer_objects.enums_swagger import CountryCodeJson, StrictnessTypeEnumJson
from txmatching.data_transfer_objects.hla.hla_swagger import HLAAntibody, HLACode
from txmatching.data_transfer_objects.hla.parsing_issue_swagger import \
    ParsingIssuePublicJson, ParsingIssueBaseJson
from txmatching.data_transfer_objects.matchings.matching_swagger import AntibodyMatchJson
from txmatching.utils.enums import HLA_GROUPS
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
