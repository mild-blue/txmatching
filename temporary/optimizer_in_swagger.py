from flask_restx import fields

from optimizer_api import optimizer_api


class DictItem(fields.Raw):
    def output(self, key, obj, *args, **kwargs):
        try:
            dct = getattr(obj, self.attribute)
        except AttributeError:
            return {}
        return dct or {}


DonorToRecipientJson = optimizer_api.model('DonorToRecipient', {
    'donor_id': fields.Integer(required=True),
    'recipient_id': fields.Integer(required=True),
    'weights': DictItem(attribute="calling_args")
})

StatisticsJson = optimizer_api.model('Statistics', {
    'number_of_selected_cycles': fields.Integer(required=True),
    'number_of_selected_chains': fields.Integer(required=True),
    'number_of_selected_transplants': fields.Integer(required=True),
    'final_level': fields.Integer(required=True),
    'aggregated_weights': DictItem(attribute="calling_args")
})

CycleOrChainJson = optimizer_api.model('CycleOrChain', {
    'arcs': fields.List(required=True, cls_or_instance=fields.Nested(DonorToRecipientJson)),
    'cycle_weights': DictItem(attribute="calling_args")
})

OptimizerReturnObjectJson = optimizer_api.model('OptimizerReturn', {
    'selected_cycles_and_chains': fields.List(required=True, cls_or_instance=fields.Nested(CycleOrChainJson)),
    'statistics': fields.Nested(StatisticsJson, reqired=True)
})

PairJson = optimizer_api.model('Pair', {
    'donor_id': fields.Integer(required=True, example=1),
    'recipient_id': fields.Integer(reqired=False, example=4)
})

OptimizerConfigurationJson = optimizer_api.model('OptimizerConfiguration', {
    'max_cycle_length': fields.Integer(reqired=False, example=3),
    'max_chain_length': fields.Integer(reqired=False, example=4),
    'objective': fields.List(required=False, cls_or_instance=DictItem(
        attribute="calling_args", example=[{"transplant_count": 1}, {"hla_compatibility_score": 3}]))
})

CompGraphEntryJson = optimizer_api.model('CompGraphEntry', {
    'donor_id': fields.Integer(required=True),
    'recipient_id': fields.Integer(required=True),
    'weights': DictItem(attribute="calling_args", example={"hla_compatibility_score": 2})
})

OptimizerRequestObjectJson = optimizer_api.model('OptimizerRequest', {
    'compatibility_graph': fields.List(required=True, cls_or_instance=fields.Nested(CompGraphEntryJson)),
    'pairs': fields.List(reqired=True, cls_or_instance=fields.Nested(PairJson)),
    'configuration': fields.Nested(OptimizerConfigurationJson, required=True)
})
