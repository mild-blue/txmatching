from flask_restx import fields

from txmatching.web.api.namespaces import matching_api

TRANSPLANT = matching_api.model('Transplant', {
    'score': fields.Float(required=True),
    'compatible_blood': fields.Boolean(required=True),
    'donor': fields.String(required=True),
    'recipient': fields.String(required=True)
})

COUNTRY_MODEL = matching_api.model('Country', {
    'country_code': fields.String(required=True),
    'donor_count': fields.Integer(required=True),
    'recipient_count': fields.Integer(required=True)
})

ROUND_MODEL = matching_api.model('Round', {
    'transplants': fields.List(cls_or_instance=fields.Nested(TRANSPLANT))
})

MatchingJson = matching_api.model('Matching', {
    'score': fields.Float(required=True),
    'rounds': fields.List(required=True, cls_or_instance=fields.Nested(ROUND_MODEL)),
    'countries': fields.List(required=True, cls_or_instance=fields.Nested(COUNTRY_MODEL))

})
