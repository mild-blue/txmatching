from flask_restx import fields

from txmatching.web.api.namespaces import enums_api

SuccessJsonOut = enums_api.model('Success', {
    'success': fields.Boolean(required=True),
})

IdentifierJsonIn = enums_api.model('Identifier', {
    'id': fields.Integer(required=True)
})

FailJson = enums_api.model('FailResponse', {
    'error': fields.String(required=True),
    'message': fields.String(required=False),
})
