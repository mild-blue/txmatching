from flask_restx import fields

from txmatching.data_transfer_objects.base_patient_swagger import (
    AllMessagesJson, DbId, DonorToUpdate, Etag, MedicalId,
    PatientParametersJson, PatientToUpdate, RecipientRequirements,
    RecipientToUpdate)
from txmatching.data_transfer_objects.enums_swagger import (BloodGroupEnumJson,
                                                            CountryCodeJson,
                                                            DonorTypeEnumJson)
from txmatching.data_transfer_objects.external_patient_upload.swagger import (
    DonorJsonIn, RecipientJsonIn)
from txmatching.data_transfer_objects.hla.hla_swagger import HLAAntibodies
from txmatching.data_transfer_objects.hla.parsing_issue_swagger import (
    ParsingIssueJson, ParsingIssuePublicJson)
from txmatching.data_transfer_objects.matchings.matching_swagger import (
    DESCRIPTION_DETAILED_SCORE, EXAMPLE_DETAILED_SCORE,
    DetailedScoreForGroupJson, RecipientDonorCompatibilityDetailsJson)
from txmatching.utils.blood_groups import BloodGroup
from txmatching.web.web_utils.namespaces import patient_api

DonorJson = patient_api.model('Donor', {**DbId, **MedicalId, **Etag, **{
    'active': fields.Boolean(required=True, description='Whether the user shall be used in pairing calculation'),
    'db_id': fields.Integer(required=True, description='Database id of the patient'),
    'medical_id': fields.String(required=True, description='Medical id of the patient'),
    'internal_medical_id': fields.String(required=False, description='Internal medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersJson),
    'donor_type': fields.Nested(DonorTypeEnumJson, required=True),
    'related_recipient_db_id': fields.Integer(required=False, description='Database id of the related recipient'),
    'score_with_related_recipient': fields.Float(required=False, description='Score calculated with related recipient'),
    'max_score_with_related_recipient': fields.Float(required=False, description='Maximum transplant score'),
    'active_and_valid_pair': fields.Boolean(required=False,
                                            description='Indication of whether the pair is included in the matching run'),
    'compatible_blood_with_related_recipient': fields.Boolean(
        required=False,
        description='Indicator whether Donor and related recipients have compatible blood groups'
    ),
    'detailed_score_with_related_recipient': fields.List(
        required=False,
        description=DESCRIPTION_DETAILED_SCORE,
        example=EXAMPLE_DETAILED_SCORE,
        cls_or_instance=fields.Nested(DetailedScoreForGroupJson)),
    'parsing_issues': fields.List(
        required=False,
        cls_or_instance=fields.Nested(ParsingIssueJson)
    ),
    'all_messages': fields.Nested(required=False, model=AllMessagesJson)
}})

RecipientJson = patient_api.model('Recipient', {**DbId, **MedicalId, **Etag, **{
    'acceptable_blood_groups': fields.List(required=False, cls_or_instance=fields.Nested(BloodGroupEnumJson),
                                           example=[BloodGroup.A.value, BloodGroup.ZERO.value]),
    'internal_medical_id': fields.String(required=False, description='Internal medical id of the patient'),
    'parameters': fields.Nested(required=True, model=PatientParametersJson),
    'hla_antibodies': fields.Nested(required=True, model=HLAAntibodies),
    'related_donors_db_ids': fields.List(required=True, cls_or_instance=fields.Integer,
                                         description='Database id of the related donor'),
    'recipient_requirements': fields.Nested(RecipientRequirements),
    'waiting_since': fields.DateTime(required=False),
    'previous_transplants': fields.Integer(required=False),
    'recipient_cutoff': fields.Integer(required=False),
    'parsing_issues': fields.List(
        required=False,
        cls_or_instance=fields.Nested(ParsingIssueJson)
    ),
    'cpra': fields.Float(required=False, description="Recipient's cPRA [%]."),
    'compatible_donors_details': fields.List(required=False, cls_or_instance=fields.Nested(RecipientDonorCompatibilityDetailsJson)),
    'all_messages': fields.Nested(required=False, model=AllMessagesJson),
}})

PatientsJson = patient_api.model('Patients', {
    'recipients': fields.List(required=False, cls_or_instance=fields.Nested(RecipientJson)),
    'donors': fields.List(required=False, cls_or_instance=fields.Nested(DonorJson))
})

UpdatedDonorJsonOut = patient_api.model('UpdatedDonor', {
    'donor': fields.Nested(required=True, model=DonorJson),
    'parsing_issues': fields.List(required=True, cls_or_instance=fields.Nested(ParsingIssuePublicJson)),
})

UpdatedRecipientJsonOut = patient_api.model('UpdatedRecipient', {
    'recipient': fields.Nested(required=True, model=RecipientJson),
    'parsing_issues': fields.List(required=True, cls_or_instance=fields.Nested(ParsingIssuePublicJson)),
})

PatientToUpdateJson = patient_api.model('PatientModelToUpdate', PatientToUpdate)

DonorToUpdateJson = patient_api.inherit('DonorModelToUpdate', PatientToUpdateJson, DonorToUpdate)

RecipientToUpdateJson = patient_api.inherit('RecipientModelToUpdate', PatientToUpdateJson, RecipientToUpdate)

RecipientCompatibilityInfoJson = patient_api.model('RecipientCompatibilityInfoJson', {
    'cPRA': fields.Float(required=True, example=95, description="recipient's cPRA [%]."),
    'compatible_donors': fields.List(required=True, cls_or_instance=fields.Integer(), example=[3, 4, 5, 7, 8, 10, 15]),
    'compatible_donors_details': fields.List(required=True, cls_or_instance=fields.Nested(RecipientDonorCompatibilityDetailsJson))
})

HLAAntibodyPairInJson = patient_api.model('HLAAntibodyPairIn', {
    'name': fields.String(required=True, example='A32', description='HLA antibody name.'),
    'mfi': fields.Integer(required=True, example=2350, description='Mean fluorescence intensity. Use exact value.'),
})

DonorModelPairInJson = patient_api.model('DonorModelPairIn', {
    'country_code': fields.Nested(CountryCodeJson, required=True),
    'donor': fields.Nested(required=True, model=DonorJsonIn),
    'recipient': fields.Nested(required=False, model=RecipientJsonIn)
})
