from flask_restx import fields

from txmatching.scorers.scorer_constants import HLA_SCORE
from txmatching.web.web_utils.namespaces import optimizer_api


class DictItem(fields.Raw):
    def output(self, key, obj, **kwargs):
        try:
            dct = getattr(obj, self.attribute)
        except AttributeError:
            return {}
        return dct or {}


DonorToRecipientJson = optimizer_api.model('DonorToRecipient', {
    'donor_id': fields.Integer(required=True),
    'recipient_id': fields.Integer(required=True),
    'score': fields.List(required=True, cls_or_instance=fields.Integer)
})

StatisticsJson = optimizer_api.model('Statistics', {
    'number_of_found_cycles_and_chains': fields.Integer(required=True),
    'number_of_found_transplants': fields.Integer(required=True)
})

CycleOrChainJson = optimizer_api.model('CycleOrChain', {
    'patients': fields.List(required=True, cls_or_instance=fields.Nested(DonorToRecipientJson)),
    'scores': fields.List(reqired=True, cls_or_instance=fields.Integer)
})

OptimizerReturnObjectJson = optimizer_api.model('OptimizerReturn', {
    'cycles_and_chains': fields.List(required=True, cls_or_instance=fields.Nested(CycleOrChainJson)),
    'statistics': fields.Nested(StatisticsJson, reqired=True)
})

PairJson = optimizer_api.model('Pair', {
    'donor_id': fields.Integer(required=True, example=1),
    'recipient_id': fields.Integer(reqired=False, example=4),
    'category': fields.String(required=False, example='Spain')
})

LimitationsJson = optimizer_api.model('Limitations', {
    'max_cycle_length': fields.Integer(reqired=False, example=3),
    'max_chain_length': fields.Integer(reqired=False, example=4),
    'custom_algorithm_settings': DictItem(attribute='calling_args', example={'max_number_of_iterations': 200})
})

OptimizerConfigurationJson = optimizer_api.model('OptimizerConfiguration', {
    'limitations': fields.Nested(LimitationsJson, reqired=False),
    'scoring': fields.List(required=False, cls_or_instance=fields.List(requred=True, cls_or_instance=DictItem(
        attribute='calling_args')), example=[[{'transplant_count': 1}],
                                             [{HLA_SCORE: 3}, {'donor_age_difference': 20}]])
})

CompGraphEntry = optimizer_api.model('CompatibilityGraphEntry', {
    'donor_id': fields.Integer(required=True, example=1),
    'recipient_id': fields.Integer(required=True, example=2),
    'weights': DictItem(attribute='calling_args', example={HLA_SCORE: 17,
                                                           'donor_age_difference': 1
                                                           })
})

OptimizerRequestObjectJson = optimizer_api.model('OptimizerRequest', {
    'compatibility_graph': fields.List(required=True, cls_or_instance=fields.Nested(CompGraphEntry)),
    'pairs': fields.List(reqired=True, cls_or_instance=fields.Nested(PairJson)),
    'configuration': fields.Nested(OptimizerConfigurationJson, required=True)
})
