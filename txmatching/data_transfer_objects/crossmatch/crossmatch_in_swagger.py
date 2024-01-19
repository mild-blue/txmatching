from flask_restx import fields

from txmatching.data_transfer_objects.base_patient_swagger import (
    ANTIBODIES_SPECIAL_EXAMPLE, ANTIGENS_AS_LISTS_SPECIAL_EXAMPLE,
    HLA_TO_ANTIBODY_EXAMPLE, HLA_TO_ANTIBODY_PARSING_ISSUES_EXAMPLE,
    HLA_TYPING_DESCRIPTION, HLAAntibodyJsonIn)
from txmatching.data_transfer_objects.hla.hla_swagger import (HLAAntibodies,
                                                              HLAAntibody,
                                                              HLACode, HLAType)
from txmatching.data_transfer_objects.hla.parsing_issue_swagger import \
    ParsingIssueBaseJson
from txmatching.data_transfer_objects.matchings.matching_swagger import \
    AntibodyMatchJson
from txmatching.utils.hla_system.hla_cadaverous_crossmatch import \
    CadaverousCrossmatchDetailsIssues
from txmatching.web.web_utils.namespaces import crossmatch_api

HLACode = crossmatch_api.clone('HlaCode', HLACode)

HLAAntibody = crossmatch_api.clone('HlaAntibody', HLAAntibody)

HLAAntibodies = crossmatch_api.clone('HlaAntibodies', HLAAntibodies)

AntibodyMatchJson = crossmatch_api.clone('AntibodyMatch', AntibodyMatchJson)

AssumedHLAType = crossmatch_api.model('AssumedHLAType', {
    'hla_type': fields.Nested(HLAType),
    'is_frequent': fields.Boolean(required=True),
})

PotentialHLATypeRaw = crossmatch_api.model('PotentialHLATypeRaw', {
    'hla_code': fields.String(required=True),
    'is_frequent': fields.Boolean(required=True),
})

CrossmatchSummaryJson = crossmatch_api.model(
    'CrossmatchSummary',
    {
        'hla_code': fields.Nested(HLACode, required=True),
        'mfi': fields.Integer(reqired=False),
        'details_and_issues': fields.List(required=False, cls_or_instance=fields.String(
            required=False, enum=[issue.value for issue in CadaverousCrossmatchDetailsIssues]))
    }
)

CrossmatchJsonIn = crossmatch_api.model(
    'CrossmatchInput',
    {
        'recipient_id': fields.String(required=False),
        'recipient_sample_id': fields.String(required=False),
        'donor_code': fields.String(required=False),
        'donor_sample_id': fields.String(required=False),
        'datetime': fields.DateTime(required=False),
        'potential_donor_hla_typing': fields.List(required=True,
                                                  cls_or_instance=fields.List(
                                                      required=True, cls_or_instance=fields.Nested(
                                                          PotentialHLATypeRaw, required=True)),
                                                  example=ANTIGENS_AS_LISTS_SPECIAL_EXAMPLE,
                                                  description=HLA_TYPING_DESCRIPTION),
        'recipient_antibodies': fields.List(required=True,
                                            description='Detected HLA antibodies of the patient. Use high resolution '
                                                        'if available. If high resolution is provided it is assumed '
                                                        'that all tested antibodies were provided. If not it is assumed'
                                                        ' that either all or just positive ones were.',
                                            cls_or_instance=fields.Nested(
                                                HLAAntibodyJsonIn
                                            ),
                                            example=ANTIBODIES_SPECIAL_EXAMPLE)
    }
)

AntibodyMatchForHLAType = crossmatch_api.model('AntibodyMatchForHLAType', {
    'assumed_hla_types': fields.List(required=True, cls_or_instance=fields.Nested(AssumedHLAType, required=True)),
    'antibody_matches': fields.List(required=False, cls_or_instance=fields.Nested(AntibodyMatchJson)),
    'summary': fields.Nested(CrossmatchSummaryJson, readonly=True),
    'is_positive_crossmatch': fields.Boolean(required=True)
})

CrossmatchJsonOut = crossmatch_api.model(
    'CrossmatchOutput',
    {
        'recipient_id': fields.String(required=False),
        'recipient_sample_id': fields.String(required=False),
        'donor_code': fields.String(required=False),
        'donor_sample_id': fields.String(required=False),
        'datetime': fields.DateTime(required=False),
        'hla_to_antibody': fields.List(required=True,
                                       cls_or_instance=fields.Nested(AntibodyMatchForHLAType),
                                       example=HLA_TO_ANTIBODY_EXAMPLE),
        'parsing_issues': fields.List(required=True,
                                      cls_or_instance=fields.Nested(ParsingIssueBaseJson),
                                      example=HLA_TO_ANTIBODY_PARSING_ISSUES_EXAMPLE),
        'is_positive_crossmatch': fields.Boolean(required=True)
    }
)

CalculateCPRAJsonIn = crossmatch_api.model(
    'CalculateCPRAInput',
    {
        'patient_id': fields.String(required=False),
        'sample_id': fields.String(required=False),
        'datetime': fields.DateTime(required=False),
        'hla_antibodies': fields.List(required=True,
                                      description='Detected HLA antibodies of the patient.',
                                      cls_or_instance=fields.Nested(
                                                HLAAntibodyJsonIn),
                                      example=ANTIBODIES_SPECIAL_EXAMPLE)
    }
)

HLAAntibodyForCPRAJson = crossmatch_api.model(
    'HLAAntibodyForCPRAJson',
    {'hla_antibody': fields.Nested(model=HLAAntibody),
     'code_sent_to_calculator': fields.String(required=False)
     }
)

CalculateCPRAJsonOut = crossmatch_api.model(
    'CalculateCPRAOutput',
    {
        'patient_id': fields.String(required=False),
        'sample_id': fields.String(required=False),
        'datetime': fields.DateTime(required=False),
        'parsed_antibodies': fields.Nested(required=True, model=HLAAntibodies),
        'parsing_issues': fields.List(required=True,
                                      cls_or_instance=fields.Nested(ParsingIssueBaseJson),
                                      example=HLA_TO_ANTIBODY_PARSING_ISSUES_EXAMPLE),
        'cpra': fields.Float(required=True),
        'unacceptable_antibodies': fields.List(required=True,
                                               cls_or_instance=fields.Nested(HLAAntibodyForCPRAJson))
    }
)
