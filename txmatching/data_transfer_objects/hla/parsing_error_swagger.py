from flask_restx import fields

from txmatching.web.web_utils.namespaces import public_api

ParsingErrorJson = public_api.model('ParsingError', {
    'hla_code_or_group': fields.String(required=False),
    'parsing_issue_detail': fields.String(required=True),
    'message': fields.String(required=True),
    # TODO: make all fields required https://github.com/mild-blue/txmatching/issues/621
    'donor_id': fields.Integer(required=False),
    'recipient_id': fields.Integer(required=False),
    'txm_event_id': fields.Integer(required=False),
})
