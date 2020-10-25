from flask_restx import fields

from txmatching.web.api.namespaces import matching_api

AntigensScoreJson = matching_api.model('AntigensScore', {
    'A': fields.List(required=True, cls_or_instance=fields.Float),
    'B': fields.List(required=True, cls_or_instance=fields.Float),
    'DR': fields.List(required=True, cls_or_instance=fields.Float)
})

AntigensJson = matching_api.model('Antigens', {
    'A': fields.List(required=True, cls_or_instance=fields.String),
    'B': fields.List(required=True, cls_or_instance=fields.String),
    'DR': fields.List(required=True, cls_or_instance=fields.String),
    'OTHER': fields.List(required=True, cls_or_instance=fields.String)
})

AntibodiesJson = matching_api.model('Antibodies', {
    'A': fields.List(required=True, cls_or_instance=fields.String),
    'B': fields.List(required=True, cls_or_instance=fields.String),
    'DR': fields.List(required=True, cls_or_instance=fields.String),
    'OTHER': fields.List(required=True, cls_or_instance=fields.String)
})

TransplantJson = matching_api.model('Transplant', {
    'score': fields.Float(required=True),
    'compatible_blood': fields.Boolean(required=True),
    'donor': fields.String(required=True),
    'recipient': fields.String(required=True),
    'antigens_score': fields.Nested(AntigensScoreJson),
    'donor_antigens': fields.Nested(AntigensJson),
    'recipient_antigens': fields.Nested(AntigensJson),
    'recipient_antibodies': fields.Nested(AntibodiesJson)
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
    'order_id': fields.Integer(required=True),
    'count_of_transplants': fields.Integer(required=True)
})
