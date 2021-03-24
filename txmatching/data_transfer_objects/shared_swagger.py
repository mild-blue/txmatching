from flask_restx import fields

from txmatching.web.web_utils.namespaces import enums_api

SuccessJsonOut = enums_api.model('Success', {
    'success': fields.Boolean(required=True),
})

IdentifierJsonIn = enums_api.model('Identifier', {
    'id': fields.Integer(required=True)
})
