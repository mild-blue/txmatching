from flask_restx import fields

from txmatching.web.web_utils.namespaces import public_api

ParsingErrorJson = public_api.model('ParsingError', {
    'hla_code': fields.String(required=True),
    'hla_code_processing_result_detail': fields.String(required=True),
    'message': fields.String(required=True),
    # TODO: make all fields required https://github.com/mild-blue/txmatching/issues/621
    'medical_id': fields.String(required=False),
    'txm_event_id': fields.Integer(required=False),
})
