from flask_restx import fields

from txmatching.web.api.namespaces import matching_api

TransplantJson = matching_api.model('Transplant', {
    'score': fields.Float(required=True),
    'compatible_blood': fields.Boolean(required=True),
    'donor': fields.String(required=True),
    'recipient': fields.String(required=True),
    'antigen_score_a': fields.Float(required=True),
    'antigen_score_b': fields.Float(required=True),
    'antigen_score_dr': fields.Float(required=True)
})

CountryInRoundJson = matching_api.model('Country', {
    'country_code': fields.String(required=True),
    'donor_count': fields.Integer(required=True),
    'recipient_count': fields.Integer(required=True)
})

RoundJson = matching_api.model('Round', {
    'transplants': fields.List(cls_or_instance=fields.Nested(TransplantJson))
})

MatchingJson = matching_api.model('Matching', {
    'score': fields.Float(required=True),
    'rounds': fields.List(required=True, cls_or_instance=fields.Nested(RoundJson)),
    'countries': fields.List(required=True, cls_or_instance=fields.Nested(CountryInRoundJson)),
    'db_id': fields.Integer(required=True),
    'order_id': fields.Integer(required=True),
    'count_of_transplants': fields.Integer(required=True)
})

Matchings = fields.List(fields.Nested(MatchingJson))
