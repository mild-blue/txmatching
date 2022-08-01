
from flask_restx import fields

from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web.web_utils.namespaces import public_api

ParsingIssuePublicJson = public_api.model('ParsingIssuePublic', {
    'hla_code_or_group': fields.String(required=True),
    'parsing_issue_detail': fields.String(required=True, enum=[parsing_issue.name for parsing_issue in ParsingIssueDetail]),
    'message': fields.String(required=True),
    'txm_event_name': fields.String(required=True),
    'medical_id': fields.String(required=True)
})

ParsingIssueJson = public_api.model('ParsingIssue', {
    'hla_code_or_group': fields.String(required=True),
    'parsing_issue_detail': fields.String(required=True),
    'message': fields.String(required=True),
    'db_id': fields.Integer(required=True),
    'txm_event_id': fields.Integer(required=True),
    'confirmed_by': fields.Integer(required=True),
    'confirmed_at': fields.Date(required=True),
    'donor_id': fields.Integer(required=False),
    'recipient_id': fields.Integer(required=False),
})