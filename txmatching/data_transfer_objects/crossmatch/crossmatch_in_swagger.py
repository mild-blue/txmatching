from flask_restx import fields

from txmatching.data_transfer_objects.base_patient_swagger import (
    ANTIGENS_EXAMPLE, HLA_TYPING_DESCRIPTION, HLAAntibodyJsonIn)
from txmatching.data_transfer_objects.hla.hla_swagger import HLAAntibody, HLAType, HLACode
from txmatching.data_transfer_objects.hla.parsing_issue_swagger import ParsingIssueBaseJson
from txmatching.data_transfer_objects.matchings.matching_swagger import AntibodyMatchJson
from txmatching.web.web_utils.namespaces import crossmatch_api

HLACode = crossmatch_api.clone("HlaCode", HLACode)

HLAAntibody = crossmatch_api.clone("HlaAntibody", HLAAntibody)

HLAType = crossmatch_api.clone("HlaType", HLAType)

AntibodyMatchJson = crossmatch_api.clone("AntibodyMatch", AntibodyMatchJson)

CrossmatchJsonIn = crossmatch_api.model(
    'CrossmatchInput',
    {
        'donor_hla_typing_list': fields.List(required=True,
                                             cls_or_instance=fields.List(
                                                required=True,
                                                cls_or_instance=fields.String,
                                                example=ANTIGENS_EXAMPLE,
                                                description=HLA_TYPING_DESCRIPTION)),
        'recipient_antibodies': fields.List(required=True,
                                            description='Detected HLA antibodies of the patient. Use high resolution '
                                                        'if available. If high resolution is provided it is assumed '
                                                        'that all tested antibodies were provided. If not it is assumed'
                                                        ' that either all or just positive ones were.',
                                            cls_or_instance=fields.Nested(
                                                HLAAntibodyJsonIn
                                            ))
    }
)

AntibodyMatchForHLAType = crossmatch_api.model('AntibodyMatchForHLAType', {
    'hla_type': fields.List(required=True, cls_or_instance=fields.Nested(HLAType, required=True)),
    'antibody_matches': fields.List(required=False, cls_or_instance=fields.Nested(AntibodyMatchJson)),
    'summary_antibody': fields.Nested(AntibodyMatchJson)
})

CrossmatchJsonOut = crossmatch_api.model(
    'CrossmatchOutput',
    {
        'hla_to_antibody': fields.List(required=True, cls_or_instance=fields.Nested(AntibodyMatchForHLAType)),
        'parsing_issues': fields.List(required=True, cls_or_instance=fields.Nested(ParsingIssueBaseJson))
    }
)
