from flask_restx import fields

from txmatching.web.web_utils.namespaces import optimizer_api

DonorToRecipientJson = optimizer_api.model('DonorToRecipient', {
    'donor_id': fields.Integer(required=True),
    'recipient_id': fields.Integer(required=True),
    'score': fields.List(required=True, cls_or_instance=fields.Integer)
})

StatisticsJson = optimizer_api.model('Statistics', {
    'number_of_found_cycles': fields.Integer(required=False),
    'number_of_found_transplants': fields.Integer(required=False)
})

OptimizerReturnObjectJson = optimizer_api.model('OptimizerReturn', {
    'cycles_and_chains': fields.List(required=True,
                                     cls_or_instance=fields.List(cls_or_instance=fields.Nested(DonorToRecipientJson))),
    'statistics': fields.Nested(StatisticsJson, reqired=True)
})
