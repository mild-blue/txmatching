from flask_restx import fields

from txmatching.web.web_utils.namespaces import public_api

ParsingIssuePublicJson = public_api.model('ParsingIssuePublic', {
    'hla_code_or_group': fields.String(required=False),
    'parsing_issue_detail': fields.String(required=True),
    'message': fields.String(required=True),
    # TODO: make all fields required https://github.com/mild-blue/txmatching/issues/621
    'medical_id': fields.String(required=False),
    'txm_event_name': fields.String(required=False),
    'confirmed_at': fields.Date(required=False),
    'confirmed_by': fields.Integer(required=False)
})

ParsingIssueJson = public_api.model('ParsingIssue', {
    'hla_code_or_group': fields.String(required=False),
    'parsing_issue_detail': fields.String(required=True),
    'message': fields.String(required=True),
    # TODO: make all fields required https://github.com/mild-blue/txmatching/issues/621
    'donor_id': fields.Integer(required=False),
    'recipient_id': fields.Integer(required=False),
    'txm_event_id': fields.Integer(required=False),
    'confirmed_at': fields.Date(required=False),
    'confirmed_by': fields.Integer(required=False)
})
